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
    
    # Constants for the sight tape
    tape_width = 0.320 * 72  # Width in points
    max_range = int(setup_data["Max range"])
    min_range = int(setup_data["Min range"])

    # Calculate the height of the sight tape in points
    inches_per_angle = setup_data["Difference of 1 & 2"] / abs((angles_data[int(setup_data["Range 1"])] - angles_data[int(setup_data["Range 2"])]))
    tape_height = angles_data[max_range] * inches_per_angle * 72 # Convert inches to points


    tape_x = c._pagesize[0] - padding - tape_width  # Right side of the page with padding
    tape_y = 750 - padding - tape_height

    # Draw the sight tape background
    c.setFillColorRGB(1, 1, 1)  # White fill color
    c.setDash(4, 2)  # Dashed line style
    c.rect(tape_x, tape_y, tape_width, tape_height, stroke=1, fill=1)
    c.setDash(1, 0)
    
   
    print("inches per full angle", inches_per_angle)

    for i in range(int(min_range), int(max_range) + 1):
        
        # Calculate the y position of the angle
        angle_y = tape_y + (angles_data[max_range] - angles_data[i]) * inches_per_angle * 72
        print("angle_y", angle_y)
        

        # Draw the range text
        if i % 10 == 0:
            c.setStrokeColorRGB(255, 0, 0) # Red color
            c.line(tape_x, angle_y, tape_x + tape_width, angle_y)
            c.setFont("Helvetica", 6)
            c.setFillColorRGB(0,0,0)
            c.drawString(tape_x + tape_width - 8, angle_y +  1, str(i))

        elif i % 5 == 0:
            c.setStrokeColorRGB(0, 255, 0) # Red color
            c.line(tape_x, angle_y, tape_x + tape_width - 10, angle_y)
            c.setFont("Helvetica", 5)
            c.setFillColorRGB(0,0,0)
            c.drawString(tape_x + tape_width - 8, angle_y - 1, str(i))

        else:
            c.setStrokeColorRGB(0, 0, 255)   # Blue color
            c.line(tape_x, angle_y, tape_x + tape_width - 15, angle_y)

    

    
if __name__ == "__main__":
    create_pdf("test.pdf", "setup.txt", "angles.txt")
