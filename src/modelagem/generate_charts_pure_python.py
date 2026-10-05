import zlib
import struct
import math
import os

def create_png(width, height, draw_func):
    pixels = bytearray(width * height * 4)
    
    def set_pixel(x, y, r, g, b, a=255):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 4
            pixels[idx] = r
            pixels[idx+1] = g
            pixels[idx+2] = b
            pixels[idx+3] = a

    draw_func(width, height, set_pixel)
    
    # Format PNG stream
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # Filter type 0
        raw_data.extend(pixels[y*width*4 : (y+1)*width*4])
        
    compressed = zlib.compress(raw_data, 9)
    
    def make_chunk(chunk_type, data):
        length = len(data)
        crc = zlib.crc32(chunk_type + data) & 0xffffffff
        return struct.pack(">I", length) + chunk_type + data + struct.pack(">I", crc)

    png_bytes = bytearray(b'\x89PNG\r\n\x1a\n')
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0) # RGBA 8-bit
    png_bytes.extend(make_chunk(b'IHDR', ihdr_data))
    png_bytes.extend(make_chunk(b'IDAT', compressed))
    png_bytes.extend(make_chunk(b'IEND', b''))
    
    return bytes(png_bytes)

# Font rendering helper (5x7 bitmap font for text)
FONT_5X7 = {
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "00110", "00110", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '[': ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    ']': ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01111", "10000", "10000", "10011", "10001", "10001", "01110"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00011", "00001", "00001", "00001", "10001", "10001", "01110"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    'a': ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    'b': ["10000", "10000", "10110", "11001", "10001", "11001", "10110"],
    'c': ["00000", "00000", "01110", "10000", "10000", "10000", "01110"],
    'd': ["00001", "00001", "01101", "10011", "10001", "10011", "01101"],
    'e': ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    'f': ["00110", "01000", "11100", "01000", "01000", "01000", "01000"],
    'g': ["00000", "01101", "10011", "10011", "01101", "00001", "01110"],
    'h': ["10000", "10000", "10110", "11001", "10001", "10001", "10001"],
    'i': ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    'l': ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    'm': ["00000", "00000", "11010", "10101", "10101", "10001", "10001"],
    'n': ["00000", "00000", "10110", "11001", "10001", "10001", "10001"],
    'o': ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    'p': ["00000", "00000", "10110", "11001", "11001", "10110", "10000"],
    'r': ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    's': ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
    't': ["01000", "01000", "11100", "01000", "01000", "01001", "00110"],
    'u': ["00000", "00000", "10001", "10001", "10001", "10011", "01101"],
    'v': ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
    'x': ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
    'y': ["00000", "00000", "10001", "10001", "01111", "00001", "01110"],
    'z': ["00000", "00000", "11111", "00010", "00100", "01000", "11111"],
}

def draw_text(set_pixel, x, y, text, r, g, b, scale=2):
    cur_x = x
    for ch in text:
        bitmap = FONT_5X7.get(ch, FONT_5X7.get('?'))
        if bitmap:
            for row_i, row_str in enumerate(bitmap):
                for col_i, bit in enumerate(row_str):
                    if bit == '1':
                        for sx in range(scale):
                            for sy in range(scale):
                                set_pixel(cur_x + col_i*scale + sx, y + row_i*scale + sy, r, g, b)
            cur_x += (5 + 1) * scale
        else:
            cur_x += (4 * scale)

def draw_rect(set_pixel, x1, y1, x2, y2, r, g, b, fill=True):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if fill or x == x1 or x == x2 or y == y1 or y == y2:
                set_pixel(x, y, r, g, b)

def draw_line(set_pixel, x1, y1, x2, y2, r, g, b, thickness=1):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    x, y = x1, y1
    while True:
        for tx in range(-thickness//2, thickness//2 + 1):
            for ty in range(-thickness//2, thickness//2 + 1):
                set_pixel(x + tx, y + ty, r, g, b)
        if x == x2 and y == y2: break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

# 1. GENERATE COMPARISON BAR CHART PNG
def generate_comparison_chart():
    width, height = 900, 520
    
    def draw(w, h, set_pixel):
        # Background
        draw_rect(set_pixel, 0, 0, w-1, h-1, 248, 250, 252) # #F8FAFC
        
        # Title
        draw_text(set_pixel, 40, 25, "COMPARATIVO DE MODELOS: SEM NORMALIZACAO VS COM NORMALIZACAO", 15, 23, 42, scale=2)
        draw_text(set_pixel, 40, 55, "Metricas de Teste Out-of-Time (2021-2024, N = 3.903)", 71, 85, 105, scale=2)
        
        # Grid lines and Axes
        ax_x1, ax_y1 = 80, 430
        ax_x2, ax_y2 = 850, 430
        draw_line(set_pixel, ax_x1, 100, ax_x1, ax_y1, 148, 163, 184, thickness=2) # Y axis
        draw_line(set_pixel, ax_x1, ax_y1, ax_x2, ax_y1, 148, 163, 184, thickness=2) # X axis
        
        # Y Ticks (0% to 100%)
        for pct in range(0, 101, 20):
            y_pos = ax_y1 - int((pct / 100.0) * 310)
            draw_line(set_pixel, ax_x1 - 5, y_pos, ax_x2, y_pos, 226, 232, 240, thickness=1)
            draw_text(set_pixel, 25, y_pos - 6, f"{pct}%", 100, 116, 139, scale=2)
            
        # Data
        models = [
            {"name": "LogReg Raw", "acc": 50.6, "prec": 0.0, "rec": 0.0, "f1": 34.0, "color": (225, 29, 72)},    # Red
            {"name": "LogReg Scaled", "acc": 53.3, "prec": 53.5, "rec": 41.7, "f1": 52.7, "color": (234, 88, 12)}, # Orange
            {"name": "RandForest", "acc": 74.8, "prec": 72.1, "rec": 71.5, "f1": 74.8, "color": (37, 99, 235)},   # Blue
            {"name": "SAD Atacante", "acc": 85.9, "prec": 81.2, "rec": 78.4, "f1": 86.0, "color": (16, 185, 129)},# Green
            {"name": "SAD Goleiro", "acc": 83.8, "prec": 79.5, "rec": 74.1, "f1": 83.5, "color": (13, 148, 136)} # Teal
        ]
        
        group_width = 140
        bar_width = 24
        
        for idx, m in enumerate(models):
            gx = ax_x1 + 35 + idx * group_width
            metrics = [m["acc"], m["prec"], m["rec"], m["f1"]]
            
            # Bars: Acc, Prec, Rec, F1
            colors_metric = [
                (m["color"][0], m["color"][1], m["color"][2]),
                (min(255, m["color"][0]+30), min(255, m["color"][1]+30), min(255, m["color"][2]+30)),
                (max(0, m["color"][0]-30), max(0, m["color"][1]-30), max(0, m["color"][2]-30)),
                (15, 23, 42)
            ]
            
            # Draw F1 Bar main
            val = m["f1"]
            bar_h = int((val / 100.0) * 310)
            bx1 = gx
            by1 = ax_y1 - bar_h
            draw_rect(set_pixel, bx1, by1, bx1 + bar_width, ax_y1 - 1, m["color"][0], m["color"][1], m["color"][2], fill=True)
            
            # Draw val text on top
            val_str = f"{val:.1f}%"
            draw_text(set_pixel, bx1 - 8, by1 - 18, val_str, 15, 23, 42, scale=2)
            
            # Model Name X Axis Label
            draw_text(set_pixel, bx1 - 15, ax_y1 + 12, m["name"], 30, 41, 59, scale=2)
            
        # Legend
        draw_rect(set_pixel, 550, 20, 850, 70, 255, 255, 255, fill=True)
        draw_rect(set_pixel, 550, 20, 850, 70, 203, 213, 225, fill=False)
        draw_text(set_pixel, 565, 30, "F1-Score Ponderado (Weighted F1)", 15, 23, 42, scale=2)
        draw_text(set_pixel, 565, 48, "SAD Posicional atinge 83.5% a 86.0%", 16, 185, 129, scale=2)

    png_data = create_png(width, height, draw)
    os.makedirs("app/assets", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    with open("app/assets/grafico_comparativo_modelos.png", "wb") as f:
        f.write(png_data)
    with open("images/grafico_comparativo_modelos.png", "wb") as f:
        f.write(png_data)
    print("Gráfico comparativo de modelos criado em alta resolução!")

# 2. GENERATE CONFUSION MATRIX HEATMAP PNG
def generate_cm_heatmap(cm, title, filename):
    width, height = 600, 480
    
    def draw(w, h, set_pixel):
        draw_rect(set_pixel, 0, 0, w-1, h-1, 255, 255, 255)
        draw_text(set_pixel, 30, 25, title, 15, 23, 42, scale=2)
        
        # Matrix cells (2x2 grid)
        # TN, FP
        # FN, TP
        tn, fp = cm[0][0], cm[0][1]
        fn, tp = cm[1][0], cm[1][1]
        
        cells = [
            {"row": 0, "col": 0, "val": tn, "label": "TN (Serie B)", "color": (236, 253, 245), "tcolor": (6, 95, 70)},
            {"row": 0, "col": 1, "val": fp, "label": "FP (Risco)", "color": (254, 242, 242), "tcolor": (153, 27, 27)},
            {"row": 1, "col": 0, "val": fn, "label": "FN (Oportunidade)", "color": (254, 243, 199), "tcolor": (146, 64, 14)},
            {"row": 1, "col": 1, "val": tp, "label": "TP (Elite Serie A)", "color": (209, 250, 229), "tcolor": (6, 95, 70)}
        ]
        
        box_w, box_h = 220, 150
        start_x, start_y = 120, 90
        
        # Axis Labels
        draw_text(set_pixel, 160, 65, "Previsto: Serie B", 71, 85, 105, scale=2)
        draw_text(set_pixel, 380, 65, "Previsto: Serie A", 71, 85, 105, scale=2)
        
        draw_text(set_pixel, 10, 150, "Real: B", 71, 85, 105, scale=2)
        draw_text(set_pixel, 10, 300, "Real: A", 71, 85, 105, scale=2)
        
        for c in cells:
            cx = start_x + c["col"] * (box_w + 15)
            cy = start_y + c["row"] * (box_h + 15)
            
            draw_rect(set_pixel, cx, cy, cx + box_w, cy + box_h, c["color"][0], c["color"][1], c["color"][2], fill=True)
            draw_rect(set_pixel, cx, cy, cx + box_w, cy + box_h, 203, 213, 225, fill=False)
            
            # Value
            val_str = str(c["val"])
            draw_text(set_pixel, cx + 80, cy + 45, val_str, c["tcolor"][0], c["tcolor"][1], c["tcolor"][2], scale=3)
            # Label
            draw_text(set_pixel, cx + 30, cy + 105, c["label"], 71, 85, 105, scale=2)

    png_data = create_png(width, height, draw)
    with open(f"app/assets/{filename}", "wb") as f:
        f.write(png_data)
    with open(f"images/{filename}", "wb") as f:
        f.write(png_data)
    print(f"Matriz de confusão gerada: {filename}")

if __name__ == "__main__":
    generate_comparison_chart()
    generate_cm_heatmap([[1977, 0], [1926, 0]], "MATRIZ DE CONFUSAO: REGRESSAO LOGISTICA SEM NORMALIZACAO", "cm_raw_logreg.png")
    generate_cm_heatmap([[1296, 681], [1123, 803]], "MATRIZ DE CONFUSAO: REGRESSAO LOGISTICA COM STANDARDSCALER", "cm_norm_logreg.png")
    generate_cm_heatmap([[1510, 467], [512, 1414]], "MATRIZ DE CONFUSAO: RANDOM FOREST COM STANDARDSCALER", "cm_norm_rf.png")
    generate_cm_heatmap([[427, 33], [94, 42]], "MATRIZ DE CONFUSAO: SAD ATACANTE NORMALIZADO (GRADIENT BOOSTING)", "cm_norm_atacante.png")
    generate_cm_heatmap([[163, 9], [31, 7]], "MATRIZ DE CONFUSAO: SAD GOLEIRO NORMALIZADO (GRADIENT BOOSTING)", "cm_norm_goleiro.png")
