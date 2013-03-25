from datetime import date
def monthList():
    def month(m):
        return {
             'name':date(2000,m,1).strftime('%B'),
             'id':m
         }
    return [month(i+1) for i in range(12)]