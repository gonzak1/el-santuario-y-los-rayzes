using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;

string mazosFolder = @"imgs/mazos";
string outputFolder = @"imgs/sheets";

const int columns = 10;

Directory.CreateDirectory(outputFolder);

var subfolders = Directory.GetDirectories(mazosFolder);

if (subfolders.Length == 0)
{
    Console.WriteLine("No se encontraron subcarpetas en imgs/mazos.");
    return;
}

foreach (var subfolder in subfolders.OrderBy(d => d))
{
    var files = Directory
        .GetFiles(subfolder, "*.png", SearchOption.TopDirectoryOnly)
        .OrderBy(f => f)
        .ToList();

    if (files.Count == 0)
    {
        Console.WriteLine($"Sin imágenes en: {subfolder}");
        continue;
    }

    string deckName = Path.GetFileName(subfolder);
    string outputFile = Path.Combine(outputFolder, $"{deckName}.png");

    using var first = Image.Load<Rgba32>(files[0]);
    int cardWidth = first.Width;
    int cardHeight = first.Height;

    // Always at least 2 rows: cap columns so at least 1 card spills to row 2
    int effectiveCols = Math.Min(columns, Math.Max(1, files.Count - 1));
    int rows = (int)Math.Ceiling(files.Count / (double)effectiveCols);

    using var sheet = new Image<Rgba32>(effectiveCols * cardWidth, rows * cardHeight);
    sheet.Mutate(ctx => ctx.BackgroundColor(Color.Black));

    for (int i = 0; i < files.Count; i++)
    {
        using var img = Image.Load<Rgba32>(files[i]);
        int x = (i % effectiveCols) * cardWidth;
        int y = (i / effectiveCols) * cardHeight;
        sheet.Mutate(ctx => ctx.DrawImage(img, new Point(x, y), 1f));
    }

    sheet.Save(outputFile);
    Console.WriteLine($"Sheet generada: {outputFile} ({files.Count} cartas, {rows} fila/s)");
}

Console.WriteLine("Listo.");
