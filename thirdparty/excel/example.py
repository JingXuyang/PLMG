
import sys
sys.path.append(r'Z:\bin\pltk\thirdparty\excel')
import xlwt

def setStyle():
    font = xlwt.Font() # Create the Font
    font.name = 'Times New Roman'
    font.bold = True
    font.underline = True
    font.italic = True
    style = xlwt.XFStyle() # Create the Style
    style.font = font 
    return style

def setAlignment():
    alignment = xlwt.Alignment() # Create Alignment
    alignment.horz = xlwt.Alignment.HORZ_CENTER # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style = xlwt.XFStyle() # Create Style
    style.alignment = alignment
    return style

    
def setCellBackgroundColor(num=5):
    pattern = xlwt.Pattern() # Create the Pattern
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern.pattern_fore_colour = num # May be: 8 through 63(test is 0~81). 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
    style = xlwt.XFStyle() # Create Style
    # Create the Pattern
    style.pattern = pattern # Add Pattern to Style
    return style

def setCellBorders(showLeft=True,showRight=True,showTop=True,showBottom=True):
    borders = xlwt.Borders() # Create Borders
    if showLeft:
        borders.left = xlwt.Borders.THIN # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
    if showRight:
        borders.right = xlwt.Borders.THIN
    if showTop:
        borders.top = xlwt.Borders.THIN
    if showBottom:
        borders.bottom = xlwt.Borders.THIN
    borders.left_colour = 0x40
    borders.right_colour = 0x40
    borders.top_colour = 0x40
    borders.bottom_colour = 0x40
    style = xlwt.XFStyle() # Create Style
    style.borders = borders # Add Borders to Style
    return style


# get string length,the chinese length is 2
def len_byte(value):
    if value is None or value == "":
        return 10
    if type(value) != int:
        length = len(value)
        utf8_length = len(value.encode('utf-8'))
        length = (utf8_length - length) / 2 + length
    else:
        length = len(str(value))
    return int(length)

def main():
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('My Sheet')
    
    style1 = setStyle()
    style2 = setAlignment()
    style3 = setCellBackgroundColor()
    style4 = setCellBorders(showLeft=False,showBottom=False)
    style5 = setCellBorders(showLeft=False,showTop=False)
    #worksheet.write(0, 0, label = 'Row 0, Column 0 Value')
    #worksheet.write(1, 0, label = 'Formatted value',style=style1)
    #worksheet.write(2, 0, label = 'Formatted value',style=style2)
    
    #worksheet.write(3, 0, label = 'Formatted value',style=style3)
    #worksheet.write(4, 0, label = 'Formatted value',style=style4)
    #worksheet.write(5, 0, label = 'Formatted value',style=style5)
    
    for i in range(100):
        s = setCellBackgroundColor(i)
        worksheet.write(i+1, 0, label = 'Formatted value',style=s)
    
    StatusList = [["Approved",11],
                  ["Retake",10],
                  ["On Hold",51],
                  ["OOP",73],
                  ["RMF",17],
                  ["-",74],
                  ["Check",48]
                 ]
    
    for j in range(len(StatusList)):
        lis = StatusList[j]
        s = setCellBackgroundColor(lis[1])
        worksheet.write(0, j, label = lis[0],style=s)
    # set cell width
    worksheet.col(0).width = 5000
    
    workbook.save('C:/Users/kaijun/Desktop/Excel_Workbook.xls')
    
main()











