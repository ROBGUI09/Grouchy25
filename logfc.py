import logging
import os
import inspect
import traceback

# Configure the logging with a custom format that includes the timestamp
logging.basicConfig(
    filename='function_calls.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Global list to store the last 5 tracebacks
last_5_tracebacks = []

# log function calls
def logfc(func):
    def wrapper(*args, **kwargs):
        # Get the function name and the module name
        function_name = func.__name__
        module_name = func.__module__
        
        # Log the function call
        logging.info(f"Calling function {function_name} in module {module_name}")
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log the return value
            logging.info(
              f"Function {function_name} returned: {result}\n" +
              ''.join(traceback.format_stack()[:-1]).replace(os.getcwd(),"")
            )

        except Exception as e:
            # Log the exception
            logging.error(f"Exception occurred in function {function_name}: {e}")
            logging.error(traceback.format_exc())
            
            # Re-raise the exception
            raise e
        
        return result
    
    return wrapper

