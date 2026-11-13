# Opening this project from GitHub

The complete nominal frozen-evaluation raw JSON exceeds GitHub's normal file-size limit and is stored using Git LFS. Other project code, reports, figures and poster files are normal Git files.

After cloning, run these commands from the repository root:

```powershell
git lfs install
git lfs pull
```

Then open `VLC_Simulation/OWC` and follow the project launch instructions. The LFS dataset should be approximately 190 MB, not a small text pointer. Existing numerical artifacts are preserved; moving the dataset to LFS did not change its contents.

Browser test profiles (cookies/login/session databases), local credentials and downloaded `scratch/poster_deps/` are excluded. Poster generation dependencies can be installed using `python -m pip install -r requirements-poster.txt`. The supplied poster template is included under `supervisor_package/poster/Template.pptx`.
