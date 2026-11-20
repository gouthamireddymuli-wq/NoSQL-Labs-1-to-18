$docx = "C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_9\Lab9_Report.docx"
$pdf  = "C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_9\Lab9_Report.pdf"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
    $doc = $word.Documents.Open($docx, $false, $true)
    $wdFormatPDF = 17
    $doc.SaveAs([ref] $pdf, [ref] $wdFormatPDF)
    $doc.Close([ref] 0)
    Write-Host "PDF exported successfully!"
}
catch {
    Write-Error $_
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
