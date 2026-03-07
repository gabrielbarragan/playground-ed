from app.core.process import CodeExecutor

class CodeExecutorHandler:
    @staticmethod
    async def execute_code(code: str):
        """
        Execute the given code in the specified programming language and return the output.
        :param code: The code to be executed.
        :param language: The programming language of the code.
        :return: The output of the executed code.
        """
        return await CodeExecutor().execute(code)