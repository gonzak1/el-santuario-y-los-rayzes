using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;

string inputFolder = @"imgs/";
string outputFile = @"imgs/sheets/deck.png";

const int columns = 5;

var files = Directory
    .GetFiles(inputFolder, "*.png")
    .OrderBy(f => f)
    .ToList();

if (files.Count == 0)
{
    Console.WriteLine("No se encontraron imágenes.");
    return;
}

using var first = Image.Load<Rgba32>(files[0]);

int cardWidth = first.Width;
int cardHeight = first.Height;

int rows = (int)Math.Ceiling(files.Count / (double)columns);

using var sheet = new Image<Rgba32>(columns * cardWidth, rows * cardHeight);

for (int i = 0; i < files.Count; i++)
{
    using var img = Image.Load<Rgba32>(files[i]);

    int x = (i % columns) * cardWidth;
    int y = (i / columns) * cardHeight;

    sheet.Mutate(ctx => ctx.DrawImage(img, new Point(x, y), 1f));
}

sheet.Save(outputFile);

Console.WriteLine("Deck generado correctamente.");