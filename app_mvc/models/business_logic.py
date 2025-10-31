
#המחלקה צריכה לטפל בעיבוד הנתונים, בחישובים ובפעולות הלוגיות
class BusinessLogic:

    @staticmethod
    def process_data(data):
        #מקבלת נתונים, מעבדת אותם ומחזירה תשובה בפורמט מסוים אם הצליח או לא
        result = {
            'status': 'success',
            'message': 'Data processed successfully',
            'data': data,
            'processed': True
        }
        return result
