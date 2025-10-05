"""
Core logic layer for processing and calculations
"""

class BusinessLogic:
    """Main business logic class"""

    @staticmethod
    def process_data(data):
        """
        Process incoming data and return results

        Args:
            data: Input data to process

        Returns:
            dict: Processed results
        """
        # Example processing logic
        result = {
            'status': 'success',
            'message': 'Data processed successfully',
            'data': data,
            'processed': True
        }
        return result

    @staticmethod
    def calculate(num1, num2, operation='add'):
        """
        Perform calculations

        Args:
            num1: First number
            num2: Second number
            operation: Operation to perform (add, subtract, multiply, divide)

        Returns:
            dict: Calculation result
        """
        operations = {
            'add': num1 + num2,
            'subtract': num1 - num2,
            'multiply': num1 * num2,
            'divide': num1 / num2 if num2 != 0 else None
        }

        result = operations.get(operation)

        return {
            'operation': operation,
            'num1': num1,
            'num2': num2,
            'result': result,
            'success': result is not None
        }
