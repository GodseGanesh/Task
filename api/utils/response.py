class ResponseHandler:

    @staticmethod
    def success(message="Success", data=None, status_code=200):
        return {
            "status": "success",
            "message": message,
            "data": data,
            "error": None
        }, status_code

    @staticmethod
    def error(message="Error", error_detail=None, status_code=400):
        return {
            "status": "error",
            "message": message,
            "data": None,
            "error": error_detail
        }, status_code
