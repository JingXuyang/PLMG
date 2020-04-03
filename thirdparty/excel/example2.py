
import sys
sys.path.append(r'Z:\bin\pltk\thirdparty\excel')
import xlwt
import copy
def setCellBackgroundColor(num=5,style=''):
    pattern = xlwt.Pattern() # Create the Pattern
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern.pattern_fore_colour = num # May be: 8 through 63(test is 0~81). 
    if not style:
        style = xlwt.XFStyle() # Create Style
    # Create the Pattern
    style.pattern = pattern # Add Pattern to Style
    return style

def setCellBorders(showLeft=True,showRight=True,showTop=True,showBottom=True,style='',borderFormat=xlwt.Borders.THIN):
    borders = xlwt.Borders() # Create Borders
    if showLeft:
        borders.left = borderFormat# May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
    if showRight:
        borders.right = borderFormat
    if showTop:
        borders.top = borderFormat
    if showBottom:
        borders.bottom = borderFormat
    borders.left_colour = 0x40
    borders.right_colour = 0x40
    borders.top_colour = 0x40
    borders.bottom_colour = 0x40
    if not style:
        style = xlwt.XFStyle() # Create Style
    style.borders = borders # Add Borders to Style
    return style

def setCellAlignment(style='',horzAlignment=xlwt.Alignment.HORZ_CENTER,vertAlignment=xlwt.Alignment.VERT_CENTER,):
    alignment = xlwt.Alignment()
    if horzAlignment:
        alignment.horz = horzAlignment
    if vertAlignment:
        alignment.vert = vertAlignment
    if not style:
        style = xlwt.XFStyle()
    style.alignment = alignment
    return style
     
def setFont(style='',name='',colorIndex=0):
    font = xlwt.Font()
    if name:
        font.name = name
    if colorIndex:
        font.colour_index = colorIndex
    if not style:
        style = xlwt.XFStyle()
    style.font = font    
    return style
    
    
def main(infoList=[]):
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('My Sheet')

    

    # for i in range(100):
        # s = setCellBackgroundColor(i)
        # worksheet.write(i+1, 0, label = 'Formatted value',style=s)
    
    StatusList = [["-",80],
                  ["None",78],
                  ["Check",48],
                  ["Retake",10],
                  ["On Hold",51],
                  ["OOP",73],
                  ["RMF",17],
                  ["Approved",50],
                 ]
    StatusDic = {}
    for i in StatusList:
        StatusDic[i[0]] = i[1]
    # specify the cell length for adding borders to the tabel             
    bordersLength = 26
    
    # row 0, add "status" color
    for j in xrange(len(StatusList)):
        lis = StatusList[j]
        s = setCellBackgroundColor(lis[1])
        s = setCellAlignment(style=s)
        #s = setFont(style=s,colorIndex=1)
        worksheet.write(0, j+15, label = lis[0],style=s)
        
    # row 1 , add black borders for cell
    for i in xrange(bordersLength):
        s = setCellBorders(showLeft=False,showTop=False,showRight=False,borderFormat=xlwt.Borders.THICK)
        
        worksheet.write(1, i, label = '',style=s)
        
    # row 2 ,null
    
    # other row, begin row3
    if infoList:
        # set cell border
        style0 = setCellBorders(showLeft=False,showBottom=False)
        style1 = setCellBorders(showLeft=False,showTop=False)
        style2 = setCellBorders(showLeft=False,showBottom=False,showRight=False)
        style3 = setCellBorders(showLeft=False,showTop=False,showRight=False)
        
        #style2 = setFont(style=style2,colorIndex=1)
        #style3 = setFont(style=style3,colorIndex=1)
        row = 3
        for info in infoList:
            name = info['name']
            frame = info['frame']
            shotList= info['shotInfo']
            
            # set "name"  "frame"
            row1 = row+1
            worksheet.write(row,0, label=name,style = style0)
            worksheet.write(row1,0, label=frame,style = style1)
            
            # set "seq/shot" , "statue colour", frame
            column = 1
            
            
            for l in shotList:
                shot,f,status = l
                
                colorIndex = StatusDic.get(status)
                
                s1 = copy.deepcopy(style2)
                s2 = copy.deepcopy(style3)
                if colorIndex:
                    s1 = setCellBackgroundColor(style=s1,num=colorIndex)
                    s2 = setCellBackgroundColor(style=s2,num=colorIndex)
                
                    
                worksheet.write(row,column, label=shot,style=s1)
                worksheet.write(row1,column, label=f,style=s2)
                column += 1
                
            # set null column cell's borders
            lenShot = len(shotList)
            nullColumnCellLength = bordersLength-lenShot-1
            for i in xrange(nullColumnCellLength):
                i = i+1+lenShot
                #print i
                worksheet.write(row,i, label="",style=style2)
                worksheet.write(row1,i, label="",style=style3)
                
            row += 2
    
    # set row 0 cell width
    #worksheet.col(0).width = 5000
    
    workbook.save('C:/Users/kaijun/Desktop/Excel_Workbook.xls')


infoList = [{"name":"Bob",
          "frame": 1093,
          "shotInfo":[["100/020",102,"Approved"],
                      ["100/030",150,"Retake"],
                      ["120/050",172,"On Hold"]]
          },
          {"name":"Dom",
          "frame": 899,
          "shotInfo":[["101/030",109,"OOP"],
                      ["105/090",250,"None"],
                      ["122/010",72,"Approved"]]
          },
          {"name":"Jeck",
          "frame": 566,
          "shotInfo":[["101/030",109,"RMF"],
                      ["105/090",250,"Check"],
                      ["122/010",72,"-"]]
          },
        ]
#main(infoList)











