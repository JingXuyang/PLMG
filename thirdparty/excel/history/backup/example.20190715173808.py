
import sys
sys.path.append(r'Z:\bin\pltk\thirdparty\excel')
import xlwt

def setStyle(style):
    font = xlwt.Font() # Create the Font
    font.name = 'Times New Roman'
    font.bold = True
    font.underline = True
    font.italic = True
    #style = xlwt.XFStyle() # Create the Style
    style.font = font 
    return style

def setAlignment(style):
    alignment = xlwt.Alignment() # Create Alignment
    alignment.horz = xlwt.Alignment.HORZ_CENTER # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    #style = xlwt.XFStyle() # Create Style
    style.alignment = alignment
    return style

    
def setCellBackgroundColor(style):
    pattern = xlwt.Pattern() # Create the Pattern
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern.pattern_fore_colour = 5 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
     # Create the Pattern
    style.pattern = pattern # Add Pattern to Style
    return style
    
def main():
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('My Sheet')
    worksheet.write(0, 0, label = 'Row 0, Column 0 Value')
    style = xlwt.XFStyle()
    setStyle(style)
    setAlignment(style)
    setCellBackgroundColor(style)
    worksheet.write(1, 0, label = 'Formatted value',style=style)
    workbook.save('C:/Users/%username%/Desktop/Excel_Workbook.xls')
    
main()
