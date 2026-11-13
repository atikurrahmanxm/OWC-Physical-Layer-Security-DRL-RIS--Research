"""One real-current channel for 4-PAM information and uniform friendly jamming.

y = h*x + g*j + n; x in {-A,-A/3,A/3,A}, j~U[-A,A], n~N(0,sigma^2).
BER uses Gray labels 00,01,11,10 and midpoint decisions. Mutual information
integrates the same conditional PDF, the uniform/Gaussian convolution. This
is a declared alternative to the paper's continuous-input rate expression.
"""
from functools import lru_cache
import numpy as np
from scipy.special import ndtr, log_ndtr, logsumexp

LEVELS = np.array([-1., -1./3., 1./3., 1.])
BITS = np.array([[0,0], [0,1], [1,1], [1,0]])
DISTANCES = np.sum(BITS[:,None,:] != BITS[None,:,:], axis=2)


def _validate(signal_peak, jammer_peak, noise_variance):
    if not np.all(np.isfinite([signal_peak,jammer_peak,noise_variance])) or signal_peak < 0 or jammer_peak < 0 or noise_variance <= 0:
        raise ValueError("Signal/jammer peaks must be finite nonnegative currents; noise variance must be positive")


def _log_density(offset, jammer_peak):
    """Noise has unit Gaussian variance; stable even in either tail."""
    if jammer_peak < 1e-7:
        return -.5*offset**2 - .5*np.log(2*np.pi)
    lo, hi = offset-jammer_peak, offset+jammer_peak
    # Phi(hi)-Phi(lo), using reflected tails when both arguments are positive.
    large = log_ndtr(np.where(lo > 0, -lo, hi))
    small = log_ndtr(np.where(lo > 0, -hi, lo))
    with np.errstate(divide='ignore', invalid='ignore'):
        return large + np.log(-np.expm1(np.minimum(0., small-large))) - np.log(2*jammer_peak)


@lru_cache(maxsize=4)
def _nodes(order):
    return np.polynomial.legendre.leggauss(order)


@lru_cache(maxsize=32768)
def pam_mutual_information(signal_peak, jammer_peak, noise_variance, order=24):
    """Bits per real channel use, integrated over output current (not capacity).

    Piecewise Gauss-Legendre quadrature resolves each Gaussian-smeared uniform
    edge; twelve-sigma tails are omitted. Caching does not use training rewards.
    """
    _validate(signal_peak,jammer_peak,noise_variance)
    if signal_peak == 0:
        return 0.
    sd = np.sqrt(noise_variance)
    a, j = signal_peak/sd, jammer_peak/sd
    centers = a*LEVELS
    edges = np.ravel(centers[:,None] + np.array([-j,j]))
    boundaries = np.unique(np.ravel(edges[:,None]+np.array([-12.,-8.,-2.,0.,2.,8.,12.])))
    nodes, weights = _nodes(order)
    widths = np.diff(boundaries)/2
    y = ((boundaries[:-1]+boundaries[1:])[:,None]/2 + widths[:,None]*nodes).ravel()
    integration_weights = (widths[:,None]*weights).ravel()
    log_conditional = _log_density(y[:,None]-centers, j)
    log_marginal = logsumexp(log_conditional,axis=1)-np.log(4.)
    differences = log_conditional-log_marginal[:,None]
    integrand = np.sum(np.exp(log_conditional)*differences,axis=1)/(4*np.log(2.))
    value = float(integration_weights @ integrand)
    if not np.isfinite(value) or value < -1e-7 or value > 2+1e-7:
        raise ArithmeticError(f"Mutual-information quadrature out of range: {value}")
    return float(np.clip(value,0.,2.))


def _normal_cdf_integral(z):
    # Integral of Phi(z). Clipping only removes cancellation roundoff in tails.
    return np.maximum(0., z*ndtr(z)+np.exp(-.5*z*z)/np.sqrt(2*np.pi))


def _survival(t, j):
    """P(U[-j,j]+N(0,1)>t); reflected evaluation avoids subtracting tiny tails."""
    t = np.asarray(t,dtype=float)
    if j < 1e-7:
        return ndtr(-t)
    return np.clip((_normal_cdf_integral(j-t)-_normal_cdf_integral(-j-t))/(2*j),0.,1.)


@lru_cache(maxsize=32768)
def pam_bit_error_rate(signal_peak, jammer_peak, noise_variance):
    """Exact Gray 4-PAM decision probabilities under the same channel PDF."""
    _validate(signal_peak,jammer_peak,noise_variance)
    if signal_peak == 0:
        return .5
    sd=np.sqrt(noise_variance)
    a,j=signal_peak/sd,jammer_peak/sd
    centers=a*LEVELS
    thresholds=np.array([-np.inf,-2*a/3,0.,2*a/3,np.inf])
    result=0.
    for sent,center in enumerate(centers):
        for detected in range(4):
            if sent==detected:
                continue
            lo,hi=thresholds[detected:detected+2]-center
            if lo>=0:
                probability=float(_survival(lo,j))-(0. if np.isinf(hi) else float(_survival(hi,j)))
            elif hi<=0:
                probability=float(_survival(-hi,j))-(0. if np.isinf(lo) else float(_survival(-lo,j)))
            else:
                probability=1-float(_survival(hi,j))-float(_survival(-lo,j))
            result += max(0.,probability)*DISTANCES[sent,detected]/8
    return float(np.clip(result,0.,.5))


@lru_cache(maxsize=32768)
def pam_bit_map_lower_bound(signal_peak,noise_variance):
    """Optimal bit-MAP BER without jamming, a valid lower bound by data processing.

    Hard symbol midpoint decisions need not minimize bit errors at low SNR.
    For Gray 4-PAM the sign bit has threshold zero; the inner/outer bit has
    thresholds +/-t, where cosh(d*t)^2=(exp(4*d^2)+3)/4, d=A/(3*sigma).
    """
    _validate(signal_peak,0.,noise_variance)
    d=signal_peak/(3*np.sqrt(noise_variance))
    if d<1e-8:
        return .5
    log_cosh=.5*np.logaddexp(4*d*d,np.log(3.))-np.log(2.)
    threshold=(log_cosh+np.log1p(np.sqrt(-np.expm1(-2*log_cosh))))/d
    sign_error=.5*(ndtr(-d)+ndtr(-3*d))
    outer_error=ndtr(threshold-3*d)-ndtr(-threshold-3*d)
    inner_error=ndtr(d-threshold)+ndtr(-d-threshold)
    return float(.5*(sign_error+.5*(outer_error+inner_error)))


def secrecy_rate(h_ab,h_ae,h_jb,h_je,w,config,noise):
    a=config.modulation_index*config.id_bias
    bob=pam_mutual_information(abs(h_ab)*a,abs(float(np.dot(h_jb,w)))*a,noise)
    eve=pam_mutual_information(abs(h_ae)*a,abs(float(np.dot(h_je,w)))*a,noise*config.eve_noise_ratio)
    return max(0.,bob-eve)*config.symbol_rate_per_hz
