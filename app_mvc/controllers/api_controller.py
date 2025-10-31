
from flask import jsonify
from app_mvc.models.business_logic import BusinessLogic

class ApiController:
    """
    הקובץ מגדיר מחלקה בשם ApiController
והיא אחראית ל־2 פעולות עיקריות באפליקציה שלך:
1. process —  BusinessLogic קולטת נתונים כלשהם מהמשתמש ומעבדת אותם דרך המחלקה .
2. health — מחזירה תגובה פשוטה שמראה שהשרת פעיל.
    """

    def __init__(self):
        self.logic = BusinessLogic()

    def process(self, data):
        """
        מה היא עושה:
        מקבלת נתונים מהלקוח 
        שולחת אותם לפונקציה פרוסס-דטה שאמורה לטפל בהם
        מחזירה ללקוח תשובה אם הצליח או לא        """
        try:
            result = self.logic.process_data(data)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    
    def health(self):
        """
        מחזירה תגובת גייסון פשוטה כדי לוודא שהשרת פעיל
        """
        return jsonify({'status': 'healthy'}), 200
