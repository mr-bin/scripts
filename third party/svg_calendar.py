__author__    = "Anatoly Rr (anatoly.rr@gmail.com)"
__version__   = "2010"
__date__      = "2009-12-31"
__copyright__ = "(c) 2010 Anatoly Rr"
__license__   = "GPL"


from calendar import Calendar # used in render_month

class SvgCalendar:

    def __init__ (self,year):

        self.year = year

        font = 'Consolas'
        
        self.style = {
            'units'  : 'mm',

            'width'  : 100,
            'height' : 70,
            
            'border-color' : '#ccc',
            
            'year-color' : '#666666',
            'year-padding-top' : 5,
            'year-padding-left': 2,    
            'year-font-family' : font,
            'year-font-size'   : 5,
            
            'month-width'  : 24,
            'month-height' : 21,
            
            'day-width'  : 23.0 / 7.0,
            'day-height' : 12.0 / 5.0,
            
            'month-margin-right' : 0,
            'month-margin-bottom' : 0,
            
            'month-font-family' : font,
            'month-font-size' : 3,
            'month-color' : '#FF9525',
            'month-padding-top' : 3,    
            
            'month-offset-top' : 5,
            
            'week-padding-top' : 6,
            'week-font-family' : font,
            'week-font-size'   : 1.5,

            'day-padding-top' : 6,
            'day-font-family' : font,
            'day-font-size'   : 2.5,
            
            'day-color' : '#000000',
            'day-holiday-color' : '#79B1D4',
            
            'week-color' : '#999',
            'week-holiday-color' : '#79B1D4',    
        }


        self.year_name = "0x" + hex(year)[2:].upper()
        self.month_names = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B', '0C']
        self.weekdays_names = ['001', '010', '011', '100', '101', '110', '111']
        self.days_names = [ "%02x" % (i + 1) for i in range (32)] 

        # tuples (month, day)
        self.holidays = [ (1,1), (1,2), (1,3), (1,4), (1,5), (1,7), (2,23), (3, 8), (4, 4), (5, 1), (5, 9), (6,12), (9, 13), (11,4)] 
        # (4, 4) - Webmasters' Day;  (9, 13) - Programmers' Day
        
        self.not_holidays = [] # [ (1,11) ] 


    def is_holiday (self, month, day, day_of_week):
        if day_of_week in [5, 6]:
            return (month, day) not in self.not_holidays
        return (month, day) in self.holidays


    def render_day (self, x, y, month, day, day_of_week):
        svg = ''
        if self.is_holiday (month, day,  day_of_week):
            color = self.style ['day-holiday-color']
        else:
            color = self.style ['day-color']
        svg += '<text x="%smm" y="%smm" font-family="\'%s\'" font-size="%smm" fill="%s" text-anchor="middle">'% (x + 0.5*self.style['day-width'], y, self.style['day-font-family'], self.style['day-font-size'], color)
        svg += '%s' % self.days_names [day-1]
        svg += '</text>'
        return svg
        
    def render_week (self, x, y):
        svg = ''
        svg += '<g>'
        for i in range (7):
            if i < 5:
                color = self.style['week-color']
            else:
                color = self.style['week-holiday-color']            
            svg += '<text x="%smm" y="%smm" font-family="\'%s\'" font-size="%smm" text-anchor="middle" fill="%s">'% (x + (i +0.5)* self.style['day-width'],y, self.style['week-font-family'], self.style['week-font-size'], color)
            svg += '%s' % (self.weekdays_names [i])
            svg += '</text>'
        svg += '</g>'
        return svg

    def render_month (self, x,y, month_no):
        svg = ''        
    
        svg += '<g>'
        svg += '<text x="%smm" y="%smm" font-family="\'%s\'" font-size="%smm" text-anchor="middle" fill="%s">'% (x + self.style['month-width']/2,y+self.style['month-padding-top'], self.style['month-font-family'], self.style['month-font-size'], self.style['month-color'])
        svg += '%s' % (self.month_names [month_no-1])
        svg += '</text>'
        svg += self.render_week (x, y+self.style['week-padding-top'])
        
        day_of_week = -1 # will start from Monday
        week_no = 0        

        c = Calendar (0)        
        for day_no in c.itermonthdays (self.year, month_no):

            day_of_week = (day_of_week + 1) % 7
            if day_of_week == 0: week_no += 1
            
            if day_no == 0: continue # month not yet started
            
            xx = x + self.style['day-width'] * (day_of_week)
            yy = y + self.style['day-padding-top'] + week_no * self.style['day-height']
            
            svg += self.render_day (xx, yy, month_no, day_no, day_of_week)
        
        svg += '</g>'
        return svg
        
        
    def render_year (self, x, y):
        svg = ''
        svg += '<g>'
        svg += '<text x="%smm" y="%smm" font-family="\'%s\'" font-size="%smm" text-anchor="middle" fill="%s">'% (x + self.style['width']/2,y+self.style['year-padding-top'], self.style['year-font-family'], self.style['year-font-size'], self.style['year-color'])
        svg += self.year_name
        svg += '</text>'
        for i in range (12):
            xx = i % 4
            yy = i / 4 
            svg += self.render_month (x+ xx*self.style['month-width'] + xx*self.style['month-margin-right'], y + self.style['month-offset-top']+ yy*self.style['month-height'] + yy*self.style['month-margin-bottom'], i+1)
        svg += '</g>'
        return svg


    def render (self):
        svg = ''
        svg += '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        svg += '<svg width="%smm" height="%smm" version="1.1" xmlns="http://www.w3.org/2000/svg"><desc>Calendar 2009</desc>' % (self.style['width'], self.style['height'])
        svg += '<g><rect x="0" y="0" width="%smm" height="%smm" rx="2.5mm" fill="#fff" stroke="%s" storke-width="0.5mm"/></g>' % (self.style['width'], self.style['height'], self.style['border-color'])
        svg += self.render_year (self.style['year-padding-left'], 0)
        svg += '</svg>'
        return svg






if __name__ == '__main__':
    
    c = SvgCalendar (2010)    

    # normal
    if 1:
        print c.render()

    # a4
    if 0:
        k = 3;
        c.style.update ({
            'units'  : 'mm',

            'border-color' : '#fff',

            'width'  : 297,
            'height' : 210, 
            
            'year-padding-top' : 6 * k,    
            'year-padding-left': 2 * k,    
            'year-font-size'   : 5 * k,
            
            'month-width'  : 21 * k ,
            'month-height' : 20 * k,
            
            'day-width'  : 22.0 * k / 7.0,
            'day-height' : 10.0 * k / 5.0,
            
            'month-margin-right' : 9,
            'month-margin-bottom' : 1,
            
            'month-font-size' : 3 * k,
            'month-padding-top' : 5 * k ,
            
            'month-offset-top' : 6 * k,
            
            'week-padding-top' : 9 * k,
            'week-font-size'   : 1.5 * k,

            'day-padding-top' : 10 * k,
            'day-font-size'   : 2 * k,
        })
        print c.render()

