from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Define dimensions and positions
padding = 36  # 0.5 inch padding
rect_width = 3.375 * 72  # inches to points
rect_height = 2.125 * 72  # inches to points
corner_radius = 10  # points
rect_x = padding
rect_y = padding
circle_diameter = 0.955 * 72  # inches to points
circle_x = rect_x + (rect_width - circle_diameter) / 2
circle_y = rect_y + (rect_height - circle_diameter) / 2

def read_angles(filename):
    angles = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split(': ')
            angles[int(key)] = float(value)
            
    return angles

def create_pdf(pdf_filename, setup_filename, angles_filename):
    # Set up canvas
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    setup_data = read_setup(setup_filename)

    # Draw setup information
    draw_info(c, setup_data)

    # Draw scale check
    draw_scales(c)

    angles_data = read_angles(angles_filename)
    print(angles_data)
    
    # Draw tapes
    draw_tapes(c, angles_data, setup_data)
    # Save the PDF
    c.save()

def draw_scales(c):

    # Add Scale Check header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(rect_x, rect_y + rect_height + 15, "Scale Check")

    # Draw rounded rectangle
    c.roundRect(rect_x, rect_y, rect_width, rect_height, corner_radius)

    # Draw circle
    c.circle(circle_x + circle_diameter / 2, circle_y + circle_diameter / 2, circle_diameter / 2)

    # Add text inside the rectangle
    c.setFont("Helvetica", 10)
    text_rect_x = rect_x + rect_width / 2
    text_rect_y = rect_y + rect_height / 2 + 50
    c.drawCentredString(text_rect_x, text_rect_y, "Credit card")

    # Add text inside the circle
    c.setFont("Helvetica", 10)
    text_circle_x = circle_x + circle_diameter / 2
    text_circle_y = circle_y + circle_diameter / 2
    c.drawCentredString(text_circle_x, text_circle_y, "US Quarter")

def read_setup(filename):
    setup_data = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().replace('"', '').split(': ')
            if key == "metric":
                setup_data[key] = value.lower() == "true"
            else:
                setup_data[key] = float(value)
    return setup_data

def draw_info(c, setup_data):

    # Define the top left position and dimensions of the table
    table_x = 36  # 0.5 inch padding
    table_y = 750  # Starting point from the top
    table_width = 300  # Adjusted width of the table to accommodate three columns
    table_height = 220  # Height of the table
    row_height = 20  # Height of each row
    col_width = table_width / 3  # Width of each column

    # Add Setup Specs header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(table_x, table_y + 10, "Setup Specs")

    # Labels for the left column
    labels = [
        "Sight height",
        "Sight radius",
        "Arrow weight",
        "Arrow length",
        "Arrow diameter",
        "Arrow speed",
        "Range 1",
        "Range 2",
        "Difference of 1 & 2",
        "Max range",
        "Min range"
    ]

    # Corresponding metric units for each label
    metric_units = [
        "cm",
        "cm",
        "grams",
        "cm",
        "mm",
        "m/s",
        "meters",
        "meters",
        "meters",
        "meters",
        "meters"
    ]

    # Corresponding imperial units for each label
    imperial_units = [
        "in",
        "in",
        "grains",
        "in",
        "in",
        "fps",
        "yds",
        "yds",
        "in",
        "yds",
        "yds"
    ]

    # Choose units based on the metric flag from setup data
    units = metric_units if setup_data.get("metric", False) else imperial_units

    # Draw table grid
    for i in range(len(labels) + 1):
        # Draw horizontal lines
        c.line(table_x, table_y - i * row_height, table_x + table_width, table_y - i * row_height)
    for i in range(4):
        # Draw vertical lines
        c.line(table_x + i * col_width, table_y, table_x + i * col_width, table_y - table_height)

    # Set font for text
    c.setFont("Helvetica", 10)

    # Populate the table with labels, actual values, and units
    for i, label in enumerate(labels):
        c.drawString(table_x + 5, table_y - (i + 1) * row_height + 5, label)
        value = setup_data.get(label, 0)  # Get the actual value from setup data, default to 0 if not found
        c.drawString(table_x + col_width + 5, table_y - (i + 1) * row_height + 5, str(value))
        c.drawString(table_x + 2 * col_width + 5, table_y - (i + 1) * row_height + 5, units[i])


def draw_tapes(c, angles_data, setup_data):
    '''
    What I need to do:

    Find the angles per inch using the Range 1, Range 2, their respective angles, and the Difference of 1 & 2

    Then draw the sight tape at the top RIGHT (next to the table with specs), using the padding as before. It should look like this. 
    It should look like a ruler with big markings every distance ending in zero, middle markings every 5, and small markings every 1.
    
    ...
    |--------|
    |---- 10 |
    |-       |
    |-       |
    |-       |
    |-       |
    |---     |
    |-       |
    |-       |
    |-       |
    |-       |
    |---- 20 |
    |...     |
    until the max range

    Picture the start of the tape as angle 0 and the end as (angles(max_range)) rounded up.
    It should be a thin rectangle of width .320 inches and height [max_range(angle) - min_range(angle) * angles_per_inch] + a little padding but not the same as the other one.
    Because of the small width, the text next to the markings should be quite small, but still readable.
    Do this to scale with real world inches (similar to the scale check) using the angles per inch. 
    
    Do this by first plotting the angles (which should be done linearly like a ruler using the angles per inch) and assigning them a distance (not necessarily linear). 
    Then draw the markings at the appropriate distances, as well as the range number for multiples of 10.

    Min range and max range are multiples of 10
    '''
    # Constants for the sight tape
    tape_width = 0.320 * 72  # Width in points
    max_range = int(setup_data.get("Max range", 120))
    min_range = int(setup_data.get("Min range", 10))

    # Calculate the height of the sight tape in points
    max_angle = angles_data[max_range]
    min_angle = angles_data[min_range]
    inches_per_angle = setup_data["Difference of 1 & 2"] / (angles_data[int(setup_data["Range 1"])] - angles_data[int(setup_data["Range 2"])])
    tape_height = angles_data[max_range] * inches_per_angle * 72  # Convert inches to points


    tape_x = c._pagesize[0] - padding - tape_width  # Right side of the page with padding
    tape_y = 750 - padding  # Starting from the bottom of the setup specs table

    # Draw the sight tape background
    c.setFillColorRGB(1, 1, 1)  # White fill color
    c.setDash(4, 2)  # Dashed line style
    c.rect(tape_x, tape_y, tape_width, tape_height, stroke=1, fill=1)
    c.setDash(1, 0)
    

    
if __name__ == "__main__":
    create_pdf("test.pdf", "setup.txt", "angles.txt")
