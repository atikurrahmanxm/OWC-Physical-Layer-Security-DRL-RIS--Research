$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$posterDir = Join-Path $projectRoot 'supervisor_package\poster'
$deckPath = Join-Path $posterDir 'Ruposhi_Bytes_Project_Poster.pptx'
$pdfPath = Join-Path $posterDir 'Ruposhi_Bytes_Project_Poster.pdf'
$previewPath = Join-Path $posterDir 'Ruposhi_Bytes_Project_Poster.png'
$powerPointApp = New-Object -ComObject PowerPoint.Application
$posterDeck = $null
try {
    $posterDeck = $powerPointApp.Presentations.Open($deckPath, $false, $false, $false)
    foreach ($posterShape in $posterDeck.Slides.Item(1).Shapes) {
        if ($posterShape.HasTextFrame -eq -1 -and $posterShape.TextFrame.HasText -eq -1) {
            $posterRange = $posterShape.TextFrame.TextRange
            $shrinkCount = 0
            while ($posterRange.BoundHeight -gt ($posterShape.Height - 1) -and $posterRange.Font.Size -gt 18 -and $shrinkCount -lt 30) {
                $posterRange.Font.Size = $posterRange.Font.Size - 0.5
                $shrinkCount++
            }
            if ($posterRange.BoundHeight -gt ($posterShape.Height + 2)) { Write-Output ('OVERFLOW: ' + $posterRange.Text.Substring(0,[Math]::Min(70,$posterRange.Text.Length))) }
        }
    }
    $posterDeck.Save()
    $posterDeck.SaveAs($pdfPath, 32)
    $posterDeck.Slides.Item(1).Export($previewPath, 'PNG', 2160, 1440)
    Write-Output $pdfPath
    Write-Output $previewPath
} finally {
    if ($posterDeck) { $posterDeck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($posterDeck) }
    $powerPointApp.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPointApp)
}
