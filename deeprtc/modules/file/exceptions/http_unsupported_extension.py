from fastapi import HTTPException


class UnsupportedExtensionHttpException(HTTPException):
    def __init__(self, extensions=None):
        detail = 'Unsupported file codec'

        if extensions:
            extensions_str = ','.join(extensions)
            detail = '{0}. Please use: {1}'.format(
                detail, extensions_str)

        super().__init__(status_code=415, detail=detail)
