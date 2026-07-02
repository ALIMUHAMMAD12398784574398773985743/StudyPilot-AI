import os
import re
from .google_adk import Agent, SessionState
from ..utils.security import sanitize_input_text

class StudyPlannerAgent(Agent):
    """
    Study Planner Agent: Generates detailed, personalized study plans.
    Integrates with Google Gemini API when available, and falls back to a 
    highly customized, robust day-by-day offline planner when offline.
    """
    def __init__(self):
        super().__init__(
            name="StudyPlannerAgent",
            instruction="You generate highly personalized, day-by-day study plans matching topic, duration, daily commitment, and academic level."
        )

    def clean_html_entities(self, text: str) -> str:
        """
        Removes HTML entities (like &quot;, &apos;, &amp;, etc.) from the output,
        replacing them with standard text equivalents or removing them.
        """
        if not text:
            return ""
        # Replace common entities
        replacements = {
            "&quot;": '"',
            "&apos;": "'",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&#39;": "'",
            "&#34;": '"'
        }
        for entity, char in replacements.items():
            text = text.replace(entity, char)
        # Regex to strip any remaining HTML entities
        text = re.sub(r"&[a-zA-Z0-9#]+;", "", text)
        return text

    def generate_plan(self, topic: str, duration_weeks: int, daily_hours: float, skill_level: str) -> str:
        """
        Generate a comprehensive, structured study plan.
        Detects if Gemini API is available. If so, uses it. Otherwise,
        runs the advanced day-by-day offline generator.
        """
        topic = sanitize_input_text(topic)
        skill_level = sanitize_input_text(skill_level)
        
        if not topic:
            return "Please provide a valid topic to create a study plan."
            
        duration_weeks = max(1, min(12, int(duration_weeks)))
        daily_hours = max(0.5, min(8.0, float(daily_hours)))
        
        # Check if Gemini API key is available
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                # Use google-genai to generate a plan via Gemini 2.5 Flash
                from google import genai
                client = genai.Client(api_key=api_key)
                
                total_days = duration_weeks * 7
                prompt = (
                    f"Generate a highly detailed, personalized day-by-day study plan for the subject: '{topic}'.\n\n"
                    f"Parameters:\n"
                    f"- Skill level: {skill_level}\n"
                    f"- Duration: {duration_weeks} Weeks ({total_days} Days)\n"
                    f"- Daily study commitment: {daily_hours} Hours per day\n\n"
                    f"Requirements:\n"
                    f"1. Generate a realistic daily schedule with specific study topics and tasks for each of the {total_days} days. "
                    f"Format each day as '### Day X: [Specific Topic Name]' followed by bullet points detailing study tasks, hands-on practice, and hours.\n"
                    f"2. Include a weekly milestone at the end of each week (e.g. '🏆 Week X Milestone: ...').\n"
                    f"3. Recommend high-quality learning resources (official documentation, specific books, or interactive tutorials) where appropriate.\n"
                    f"4. Do NOT output HTML entities like &quot;, &apos;, &amp;, &lt;, or &gt;. Return clean, standard markdown.\n"
                    f"5. Maintain clean, professional, human-readable formatting."
                )
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response and response.text:
                    cleaned_plan = self.clean_html_entities(response.text)
                    return cleaned_plan
            except Exception as e:
                # Log API error and proceed to fallback offline generator
                print(f"Gemini API Planner Exception: {str(e)}. Falling back to offline generator.")
        
        # Offline simulation fallback (detailed day-by-day builder)
        return self._generate_plan_offline(topic, duration_weeks, daily_hours, skill_level)

    def _get_topic_details(self, daily_topic: str, skill_level: str, daily_hours: float) -> dict:
        """
        Returns a dictionary containing a distinct 'focus', 'task', and 'practice' 
        for a given daily topic. Uses a predefined lookup for common topics, 
        and falls back to dynamic, keyword-based or generic generation for others.
        """
        # Predefined lookup for core subjects to guarantee rich, non-repetitive tasks.
        lookup = {
            "Variables & Data Types": {
                "Beginner": {
                    "focus": "Understanding how Python stores values in memory and distinguishing basic types (int, float, str, bool).",
                    "task": "Declare various variables, learn about dynamic typing, and practice type conversion (casting).",
                    "practice": "Write a script that prompts for user information, converts inputs to appropriate types, and prints a formatted summary."
                },
                "Intermediate": {
                    "focus": "Deep dive into variable scopes (LEGB rule) and mutable vs. immutable data types.",
                    "task": "Analyze memory IDs using id() and verify which objects can be modified in-place.",
                    "practice": "Write code demonstrating list mutability side-effects when passed to functions and how to prevent them using copying."
                },
                "Advanced": {
                    "focus": "Investigating Python memory management, object reference counts, and garbage collection internals.",
                    "task": "Use the sys and gc modules to measure object sizes and track reference counting behavior.",
                    "practice": "Build a memory profiler utility that tracks memory allocations for dynamic data structure growth."
                }
            },
            "Operators & Basic Math": {
                "Beginner": {
                    "focus": "Applying arithmetic, comparison, and logical operators in expressions.",
                    "task": "Learn operator precedence, modulo division, integer division, and boolean logic chaining.",
                    "practice": "Create a console calculator that handles basic arithmetic operations and checks for division by zero."
                },
                "Intermediate": {
                    "focus": "Utilizing bitwise operators and short-circuit evaluation logic.",
                    "task": "Study how AND/OR operators short-circuit and how to perform bitwise shifting in Python.",
                    "practice": "Write a permission check system utilizing bitwise flags (Read, Write, Execute)."
                },
                "Advanced": {
                    "focus": "Overloading operators in custom classes to define custom math or comparison behaviors.",
                    "task": "Explore magic methods like __add__, __sub__, __mul__, and custom comparison dunders.",
                    "practice": "Implement a custom 2D Vector class supporting vector addition, subtraction, scalar multiplication, and equality checks."
                }
            },
            "Control Flow: If-Else": {
                "Beginner": {
                    "focus": "Making decisions in code using if, elif, and else statements.",
                    "task": "Write conditional blocks and nested if-statements based on boolean conditions.",
                    "practice": "Build a grading program that translates numerical scores to letter grades with validator logic."
                },
                "Intermediate": {
                    "focus": "Using conditional expressions (ternary operators) and the match-case statement (Python 3.10+).",
                    "task": "Refactor nested if-else blocks into clean match-case statements and conditional assignments.",
                    "practice": "Implement a state machine or request handler using match-case patterns."
                },
                "Advanced": {
                    "focus": "Optimizing conditional branches and utilizing design patterns to eliminate deep nested conditionals.",
                    "task": "Study the Strategy pattern and dictionary dispatching as cleaner alternatives to complex conditional ladders.",
                    "practice": "Refactor a legacy conditional-heavy calculator into a dispatcher map of execution strategies."
                }
            },
            "Loops: For & While": {
                "Beginner": {
                    "focus": "Iterating over collections using for loops and repeating tasks with while loops.",
                    "task": "Learn loop syntax, range() function usage, and preventing infinite loops in while blocks.",
                    "practice": "Write a script that prints a multiplication table and another that prompts for a password until correct."
                },
                "Intermediate": {
                    "focus": "Iterating using enumerate(), zip(), and understanding the else clause in loops.",
                    "task": "Use advanced iteration utilities and implement custom while loops that monitor process timeouts.",
                    "practice": "Write a data alignment tool that merges two lists of different lengths using zip_longest."
                },
                "Advanced": {
                    "focus": "Custom iterators and generator functions utilizing yield.",
                    "task": "Study generator performance advantages, memory footprints, and the Iterator protocol.",
                    "practice": "Write a memory-efficient log parser generator that reads multi-gigabyte log files line-by-line."
                }
            },
            "Loop Control (Break, Continue)": {
                "Beginner": {
                    "focus": "Altering loop execution flow dynamically with break and continue statements.",
                    "task": "Learn how to immediately exit loops or skip the rest of the current iteration.",
                    "practice": "Write a prime number checker that exits the loop early once a divisor is found."
                },
                "Intermediate": {
                    "focus": "Error handling and retry loops with break controls.",
                    "task": "Combine try-except blocks inside loops, using break on success and continue/sleep on failure.",
                    "practice": "Implement an API retry script that attempts a network request up to 3 times before failing."
                },
                "Advanced": {
                    "focus": "Implementing custom retry backoff strategies using loop controllers.",
                    "task": "Model exponential backoff logic using loops, break controls, and exception tracking.",
                    "practice": "Build a resilient file uploader that retries chunk uploads with jittered backoff."
                }
            },
            "String Methods & Formatting": {
                "Beginner": {
                    "focus": "Manipulating text and formatting output using f-strings and basic string methods.",
                    "task": "Learn strip(), split(), join(), replace(), lower(), and upper(), and f-string syntax.",
                    "practice": "Write a text parsing script that sanitizes raw user input by removing whitespace and censoring bad words."
                },
                "Intermediate": {
                    "focus": "Advanced f-string formatting, alignment, and string template structures.",
                    "task": "Format numbers, percentages, dates, and build multi-line template emails dynamically.",
                    "practice": "Generate a text-based financial report table with perfectly aligned columns and currency formatting."
                },
                "Advanced": {
                    "focus": "Regular expressions for complex string extraction and replacement.",
                    "task": "Study the re module, capturing groups, and greedy vs. non-greedy matching.",
                    "practice": "Build a robust parser that extracts and validates email addresses, phone numbers, and dates from unstructured text."
                }
            },
            "Week 1 Review & Core Syntax Check": {
                "Beginner": {
                    "focus": "Reviewing all fundamentals: variables, operators, loops, control flow, and strings.",
                    "task": "Solve various syntax and logic exercises covering the week's concepts.",
                    "practice": "Build a 'Guess the Number' CLI game that brings together loops, conditionals, and variables."
                },
                "Intermediate": {
                    "focus": "Refactoring basic syntax into clean, standard code blocks adhering to PEP 8.",
                    "task": "Audit code snippets for formatting, naming conventions, and logic optimization.",
                    "practice": "Take a poorly written script, document its flaws, and refactor it into clean, idiomatic code."
                },
                "Advanced": {
                    "focus": "Profiling and benchmarking core syntax elements for performance differences.",
                    "task": "Compare execution speeds of loops vs. list comprehensions vs. map() using the timeit module.",
                    "practice": "Produce a benchmark report detailing the most efficient way to process simple lists."
                }
            },
            "Working with Lists": {
                "Beginner": {
                    "focus": "Storing and accessing ordered data collections using Python lists.",
                    "task": "Understand indexing, slicing, appending, inserting, removing, and sorting lists.",
                    "practice": "Build a simple to-do list manager that allows users to add, view, and delete tasks."
                },
                "Intermediate": {
                    "focus": "List comprehensions and multidimensional lists.",
                    "task": "Write clean list comprehensions to filter and transform data, and manage nested matrix data.",
                    "practice": "Create a matrix transposition utility using nested list comprehensions."
                },
                "Advanced": {
                    "focus": "Underlying array-list implementation, time complexities (amortized O(1)), and memory usage.",
                    "task": "Study list memory resizing behavior using sys.getsizeof() and list copy vs deepcopy.",
                    "practice": "Implement a custom dynamic array class that grows its capacity when filled."
                }
            },
            "Tuples & Sets": {
                "Beginner": {
                    "focus": "Understanding immutable tuples and unique item sets.",
                    "task": "Learn when to use tuples instead of lists, and use sets for membership testing.",
                    "practice": "Write a script that takes a list of duplicates and returns only the unique items using a set."
                },
                "Intermediate": {
                    "focus": "Set operations (union, intersection, difference) and named tuples.",
                    "task": "Practice combining datasets using set operations and restructure record data using namedtuples.",
                    "practice": "Build a user permission comparator that identifies common and unique permissions between two users."
                },
                "Advanced": {
                    "focus": "Hashability requirements for set elements and dictionary keys.",
                    "task": "Analyze how Python uses hashing for O(1) set lookups and implement __hash__ in a custom class.",
                    "practice": "Write an efficient deduplication engine that compares massive datasets using custom hashed records."
                }
            },
            "Dictionaries & Key-Value pairs": {
                "Beginner": {
                    "focus": "Mapping keys to values using Python dictionaries.",
                    "task": "Learn dictionary creation, accessing keys safely using get(), updating values, and iteration.",
                    "practice": "Write a word frequency counter that parses a sentence and counts the occurrences of each word."
                },
                "Intermediate": {
                    "focus": "Dictionary comprehensions, default dicts, and nested dictionary structures.",
                    "task": "Construct complex nested maps, use collections.defaultdict, and merge dictionaries.",
                    "practice": "Build an inventory management system with nested item categories and stock-level alerts."
                },
                "Advanced": {
                    "focus": "Hash map collision resolution and dictionary preservation of insertion order (Python 3.7+).",
                    "task": "Read about dict implementation detail changes and compare dict memory layout to slots.",
                    "practice": "Implement a custom LRU (Least Recently Used) cache using a dictionary and a doubly linked list."
                }
            },
            "Custom Functions & Scope": {
                "Beginner": {
                    "focus": "Writing reusable blocks of code using functions.",
                    "task": "Learn def keyword, function parameters, return values, and global vs. local scope.",
                    "practice": "Write functions to convert temperatures (C to F) and calculate invoice totals with tax."
                },
                "Intermediate": {
                    "focus": "Function arguments (*args, **kwargs), default parameters, and closure scopes.",
                    "task": "Define flexible function interfaces and nested functions that capture enclosing scope variables.",
                    "practice": "Create a customizable logger function that returns specialized log message formatters."
                },
                "Advanced": {
                    "focus": "Functional programming patterns, higher-order functions, and decorators.",
                    "task": "Write custom decorators that log function arguments, execution time, or enforce authentication.",
                    "practice": "Build a cache/memoization decorator from scratch that caches function output based on input arguments."
                }
            },
            "Built-in Functions & Modules": {
                "Beginner": {
                    "focus": "Importing code from modules and utilizing built-in functions.",
                    "task": "Learn import statement, using math, random, and datetime modules, and built-ins like sum(), len(), min(), max().",
                    "practice": "Write a script that simulates rolling dice and calculates statistical distributions."
                },
                "Intermediate": {
                    "focus": "Creating custom modules/packages and using standard library gems (itertools, collections).",
                    "task": "Structure multiple files into a package, and use counter, deque, and permutations.",
                    "practice": "Build a schedule solver that uses itertools.permutations to find optimal task orderings."
                },
                "Advanced": {
                    "focus": "Dynamic imports, namespace packages, and custom module loaders.",
                    "task": "Explore __import__, importlib, and inspecting module contents dynamically using inspect.",
                    "practice": "Write a plugin loader that scans a directory for python files and automatically loads their classes."
                }
            },
            "Error & Exception handling (Try/Except)": {
                "Beginner": {
                    "focus": "Handling runtime errors gracefully using try/except blocks.",
                    "task": "Learn about exception types (ValueError, TypeError, ZeroDivisionError) and basic error printouts.",
                    "practice": "Build a safe user input reader that prompts for integers and keeps retrying without crashing."
                },
                "Intermediate": {
                    "focus": "Chaining exceptions, custom exception classes, and else/finally blocks.",
                    "task": "Define domain-specific exceptions, catch multiple error classes, and ensure resource cleanups.",
                    "practice": "Create a bank account simulator that raises custom InsufficientFundsError on overdraws."
                },
                "Advanced": {
                    "focus": "Exception traceback inspection, context managers, and exit hook protocols.",
                    "task": "Write custom context managers using __enter__ and __exit__ to handle database transaction rollbacks.",
                    "practice": "Build a safe SQL transaction simulator that commits on success and rolls back on exception."
                }
            },
            "Mini Command-line Project": {
                "Beginner": {
                    "focus": "Applying variables, collections, functions, and loops to build a console app.",
                    "task": "Design a text-based user menu flow, handle inputs, and store data in memory.",
                    "practice": "Build a fully operational task manager CLI where users can add, remove, and toggle tasks."
                },
                "Intermediate": {
                    "focus": "Integrating external inputs/outputs and structuring code into multiple files.",
                    "task": "Design modular code layout, implement arguments parser, and save app state to a JSON file.",
                    "practice": "Build a CLI contact book that reads and writes data to a local JSON file, supporting searches."
                },
                "Advanced": {
                    "focus": "Building an extensible CLI utility with logging, config files, and tests.",
                    "task": "Use argparse, configparser, logging, and unit tests to create a professional command-line tool.",
                    "practice": "Create a command-line developer environment setup manager that checks dependencies."
                }
            },
            "Classes & Objects": {
                "Beginner": {
                    "focus": "Understanding object-oriented programming concepts and class definitions.",
                    "task": "Learn class keyword, instantiating objects, and defining methods.",
                    "practice": "Create a Book class with attributes like title, author, and pages, and a method to print its info."
                },
                "Intermediate": {
                    "focus": "Distinguishing instance attributes vs class attributes and instance vs class methods.",
                    "task": "Use @classmethod and @staticmethod decorators to define helper methods.",
                    "practice": "Build a Student registration system where a class variable tracks total student count."
                },
                "Advanced": {
                    "focus": "Metaclasses, class creation hook, and dynamic class generation.",
                    "task": "Study type() function as a class generator and write a custom metaclass to enforce naming constraints.",
                    "practice": "Implement a simple ORM model metaclass that maps class attributes to database columns."
                }
            },
            "Attributes & Custom Methods": {
                "Beginner": {
                    "focus": "Defining class properties and functions to interact with object data.",
                    "task": "Write methods that mutate object state based on inputs.",
                    "practice": "Create a BankAccount class with balance, and methods for deposit() and withdraw()."
                },
                "Intermediate": {
                    "focus": "Using property decorators (@property, @setter) for data validation.",
                    "task": "Implement encapsulation using private attributes (single and double underscore prefixes).",
                    "practice": "Build a Temperature class that exposes Celsius and Fahrenheit conversion via property getters/setters."
                },
                "Advanced": {
                    "focus": "Custom descriptor classes and controlling attribute access overrides.",
                    "task": "Explore __getattr__, __setattr__, and building descriptor classes implementing __get__ and __set__.",
                    "practice": "Write a validation descriptor that automatically checks if string attributes match specific regex rules."
                }
            },
            "Constructor (__init__)": {
                "Beginner": {
                    "focus": "Initializing object state at instantiation time.",
                    "task": "Learn about the __init__ method, passing arguments, and setting default attribute values.",
                    "practice": "Create a Car class that requires make, model, and year, and initializes mileage to zero."
                },
                "Intermediate": {
                    "focus": "Alternative constructors using class methods, and initializing complex states.",
                    "task": "Write factory classmethods that create object instances from JSON strings or files.",
                    "practice": "Extend the Car class with a method from_string() that parses 'Toyota,Corolla,2022' into an object."
                },
                "Advanced": {
                    "focus": "Object lifecycle management, __new__ method, and singleton patterns.",
                    "task": "Understand the difference between __new__ (allocation) and __init__ (initialization).",
                    "practice": "Implement a DatabaseConnection class using a Singleton pattern to prevent multiple active connections."
                }
            },
            "Inheritance & Subclasses": {
                "Beginner": {
                    "focus": "Reusing code across classes by inheriting properties and methods.",
                    "task": "Learn base classes, subclasses, and basic inheritance structures.",
                    "practice": "Create an Animal base class and Dog/Cat subclasses that override a make_sound() method."
                },
                "Intermediate": {
                    "focus": "Using super() to call parent constructor and methods, and multiple inheritance.",
                    "task": "Learn about Method Resolution Order (MRO) and mixin classes.",
                    "practice": "Create a custom LoggableMixin class that adds logging support to arbitrary subclasses."
                },
                "Advanced": {
                    "focus": "Abstract base classes (ABCs) and interface enforcement.",
                    "task": "Use the abc module and @abstractmethod decorator to define strict abstract contracts.",
                    "practice": "Design a PaymentProcessor ABC with subclasses for Stripe and PayPal implementing all interface methods."
                }
            },
            "Method Overriding": {
                "Beginner": {
                    "focus": "Redefining base class methods inside subclasses.",
                    "task": "Understand how Python resolves methods in inherited classes.",
                    "practice": "Define a Shape class with area() returning 0, and Rectangle/Circle subclasses returning actual calculations."
                },
                "Intermediate": {
                    "focus": "Extending base class methods rather than completely replacing them.",
                    "task": "Call super().method() inside the overridden method to run parent code alongside subclass code.",
                    "practice": "Create an Employee base class and Manager subclass where Manager.get_salary() adds a bonus to the base."
                },
                "Advanced": {
                    "focus": "Cooperative multiple inheritance and resolving complex MRO issues.",
                    "task": "Trace method resolution orders in diamond-inheritance schemas using Class.__mro__.",
                    "practice": "Refactor a multi-inherited graphics class structure to avoid double-invocation of parent methods."
                }
            },
            "Polymorphism & Encapsulation": {
                "Beginner": {
                    "focus": "Hiding internal details and writing code that works with different object types.",
                    "task": "Learn how duck typing allows functions to interact with any object that implements a specific method.",
                    "practice": "Write a function render_shapes(shapes) that calls draw() on an array of different shape objects."
                },
                "Intermediate": {
                    "focus": "Enforcing access controls and interface boundaries.",
                    "task": "Learn naming conventions for internal variables and use setters to validate data ranges.",
                    "practice": "Build a secure UserAccount class where password hash is protected and username updates are validated."
                },
                "Advanced": {
                    "focus": "Abstract data type definitions and memory optimization via slots.",
                    "task": "Study how __slots__ limits dynamic attribute creation and optimizes memory layouts.",
                    "practice": "Define a high-performance Point class using __slots__ and measure its memory usage relative to standard classes."
                }
            },
            "Building an OOP CLI App": {
                "Beginner": {
                    "focus": "Integrating OOP principles into a cohesive console project.",
                    "task": "Model system entities as classes and write a controller class to manage app state.",
                    "practice": "Build an Inventory system with Product, Category, and InventoryManager classes."
                },
                "Intermediate": {
                    "focus": "Layering project architecture: Data access, business logic, and presentation classes.",
                    "task": "Separate data persistence, operations logic, and CLI menu layout into distinct class files.",
                    "practice": "Build a Library Catalog system featuring Book, Member, and Transaction classes with JSON state loading."
                },
                "Advanced": {
                    "focus": "Building a modular, plugin-based OOP application.",
                    "task": "Design a system that accepts custom extensions or plugins conforming to an ABC interface.",
                    "practice": "Create a command task runner that loads custom Task plugins dynamically from an extension folder."
                }
            },
            "Reading Text Files": {
                "Beginner": {
                    "focus": "Reading data from external files into Python.",
                    "task": "Learn the open() function, 'r' mode, read(), readline(), and using 'with' context managers.",
                    "practice": "Write a script that reads a text file and prints its contents alongside line numbers."
                },
                "Intermediate": {
                    "focus": "Handling file encoding and processing large files efficiently.",
                    "task": "Specify encoding='utf-8' and stream files line-by-line in loops to conserve memory.",
                    "practice": "Write an analyzer that parses a heavy access log file to count hits for particular IP addresses."
                },
                "Advanced": {
                    "focus": "Low-level OS operations, buffering, and memory mapping.",
                    "task": "Compare standard file reads against memory-mapped files using the mmap module.",
                    "practice": "Build a binary file inspector that reads and prints specific offsets from large binary database files."
                }
            },
            "Writing & Appending Data": {
                "Beginner": {
                    "focus": "Saving text output to files from Python.",
                    "task": "Learn 'w' and 'a' modes in open() and using write() and writelines().",
                    "practice": "Create a journal app that prompts for text and appends entries to a journal.txt file."
                },
                "Intermediate": {
                    "focus": "Temporary file storage and atomic file writing.",
                    "task": "Use the tempfile module to write temporary files and implement atomic replacements.",
                    "practice": "Write a utility that updates a configuration file safely by writing a temp file first and renaming it."
                },
                "Advanced": {
                    "focus": "File locking and concurrent file writes.",
                    "task": "Study portalocker or fcntl for cross-process file locks, ensuring data safety.",
                    "practice": "Build a logging system that multiple python scripts can safely write to concurrently using file locks."
                }
            },
            "Working with JSON Files": {
                "Beginner": {
                    "focus": "Parsing and writing structured JSON data.",
                    "task": "Learn the json module, json.load(), json.loads(), json.dump(), and json.dumps().",
                    "practice": "Write a script that loads a user configuration JSON, updates a setting, and saves it back."
                },
                "Intermediate": {
                    "focus": "Custom serialization and handling complex object types.",
                    "task": "Implement a custom JSON encoder class to serialize custom classes (e.g. datetimes or objects).",
                    "practice": "Write a system that stores and recovers a list of custom Transaction class instances in a JSON file."
                },
                "Advanced": {
                    "focus": "Performance optimizations for massive JSON structures.",
                    "task": "Compare built-in json performance against rapidjson or orjson, and explore streaming JSON parsers.",
                    "practice": "Write a parser that decodes and filters elements from a multi-gigabyte JSON database using orjson."
                }
            },
            "Introduction to Package Managers (pip)": {
                "Beginner": {
                    "focus": "Installing and using third-party packages in Python.",
                    "task": "Learn pip install, requirements.txt, and utilizing external packages.",
                    "practice": "Install requests and write a script to download a webpage's source code."
                },
                "Intermediate": {
                    "focus": "Managing project dependencies and virtual environments.",
                    "task": "Create virtual environments (venv), export requirements using pip freeze, and manage environment variables.",
                    "practice": "Set up a clean virtual environment, install select libraries, and write a setup guide."
                },
                "Advanced": {
                    "focus": "Publishing packages and managing modern build systems (Poetry/Pipenv).",
                    "task": "Learn pyproject.toml structure, packaging tools (setuptools/twine), and dependency resolution.",
                    "practice": "Pack a custom math library into a distributable wheel package and verify its installation."
                }
            },
            "Making HTTP requests": {
                "Beginner": {
                    "focus": "Communicating with web servers and consuming web APIs.",
                    "task": "Learn GET and POST requests, status codes, query parameters, and extracting JSON responses.",
                    "practice": "Write a script that queries a public weather API and displays weather alerts."
                },
                "Intermediate": {
                    "focus": "Handling request timeouts, custom headers, and session objects.",
                    "task": "Create a requests.Session, handle HTTP errors using raise_for_status(), and set connection limits.",
                    "practice": "Build a client that authenticates against a mock API and performs CRUD operations using session cookies."
                },
                "Advanced": {
                    "focus": "Asynchronous HTTP requests and connection pools.",
                    "task": "Use aiohttp or httpx to execute multiple HTTP requests concurrently in an event loop.",
                    "practice": "Build a high-performance web scraper that fetches data from 50 target pages in parallel using asyncio."
                }
            },
            "Building REST APIs with FastAPI": {
                "Beginner": {
                    "focus": "Creating simple web services and REST endpoints in Python.",
                    "task": "Learn FastAPI setup, path/query parameters, and running a server with uvicorn.",
                    "practice": "Build a hello-world API that exposes /greet and /calculator routes."
                },
                "Intermediate": {
                    "focus": "Pydantic models, request validation, and status code overrides.",
                    "task": "Define request/response schemas using Pydantic, and handle invalid requests with automatic validations.",
                    "practice": "Create a mock user management API with POST /users and GET /users/{id} endpoints."
                },
                "Advanced": {
                    "focus": "FastAPI dependency injection, custom middleware, and JWT authentication.",
                    "task": "Write dependency checkers for API keys and setup middleware that logs request execution times.",
                    "practice": "Build a secure REST API with route permissions, token generation, and database session injections."
                }
            },
            "Final Capstone Project Refinement": {
                "Beginner": {
                    "focus": "Consolidating all learned core concepts into a single capstone application.",
                    "task": "Refactor code to use files, functions, and proper control flows.",
                    "practice": "Build and document a console-based personal finance tracker with file logging and reporting."
                },
                "Intermediate": {
                    "focus": "Structuring the capstone project into packages with OOP and error handling.",
                    "task": "Create a clean repository, write README documentation, and write unit tests.",
                    "practice": "Refactor the library system into a package and achieve 80% test coverage using pytest."
                },
                "Advanced": {
                    "focus": "Optimizing, packaging, and deploying the capstone project.",
                    "task": "Write Dockerfile configurations, configure CI/CD actions, and set up linters.",
                    "practice": "Deploy your final FastAPI application code, configure automated tests, and format with black/flake8."
                }
            }
        }

        # Clean topic key to look up
        clean_topic = daily_topic.strip()
        
        # Try exact lookup
        if clean_topic in lookup and skill_level in lookup[clean_topic]:
            return lookup[clean_topic][skill_level]

        # Keyword-based mapping to generate specific tasks for common programming/CS concepts
        lower_topic = clean_topic.lower()
        matched_details = None
        
        if "jvm" in lower_topic or "virtual machine" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Understanding Java Virtual Machine (JVM), JRE, and JDK components.",
                    "task": "Install the JDK, configure environment variables, and compile a 'Hello World' using javac.",
                    "practice": "Compile and run a Java program manually via command line, inspecting the generated .class bytecode."
                },
                "Intermediate": {
                    "focus": "Investigating JVM memory architecture (Stack vs. Heap) and class loaders.",
                    "task": "Study how classes are loaded and where variables are allocated in memory.",
                    "practice": "Use command line flags (like -verbose:class) to monitor JVM class loading behavior."
                },
                "Advanced": {
                    "focus": "Garbage collection algorithms and JVM performance tuning.",
                    "task": "Analyze GC logs and learn about tuning flags (e.g. -Xms, -Xmx, -XX:+UseG1GC).",
                    "practice": "Build a simulation that triggers OutOfMemoryError and analyze heap dumps using VisualVM."
                }
            }
        elif "variable" in lower_topic or "primitive" in lower_topic or "data type" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Differentiating primitive data types (int, double, char, boolean) and object references.",
                    "task": "Write declarations for all primitive types, testing their boundaries and type limits.",
                    "practice": "Build a conversion tool that performs safe and unsafe type casting (widening vs narrowing)."
                },
                "Intermediate": {
                    "focus": "Wrapper classes, autoboxing/unboxing, and value vs. reference comparison.",
                    "task": "Study the difference between == and .equals(), and how Integer caching works in Java/Python.",
                    "practice": "Write code containing comparison edge cases for boxed objects and explain the outcomes."
                },
                "Advanced": {
                    "focus": "Memory footprint of types, value types proposals, and low-level representations.",
                    "task": "Analyze memory allocation overhead for object wrappers compared to raw primitives.",
                    "practice": "Write a performance benchmark using microbenchmarking tools (like JMH) comparing primitive vs. boxed array iterations."
                }
            }
        elif "operator" in lower_topic or "math" in lower_topic or "arithmetic" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Applying arithmetic and logical operators.",
                    "task": "Learn operator precedence, compound assignments, and increments (post vs pre).",
                    "practice": "Create a console calculator that validates inputs and performs operations."
                },
                "Intermediate": {
                    "focus": "Bitwise operators and masking.",
                    "task": "Study binary representation, logical shifts, and bitwise AND/OR/XOR operations.",
                    "practice": "Implement a flags controller utilizing bitwise masks to manage system properties."
                },
                "Advanced": {
                    "focus": "Numerical accuracy, floating-point representations, and big numbers (BigDecimal).",
                    "task": "Explore IEEE 754 float problems and how to perform exact arithmetic using BigDecimal/Fraction objects.",
                    "practice": "Write a financial interest calculator ensuring no rounding or precision errors occur."
                }
            }
        elif "if" in lower_topic or "condition" in lower_topic or "switch" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Implementing conditional logic branches.",
                    "task": "Learn if-else blocks, switch-case syntax, and logical evaluation rules.",
                    "practice": "Build a decision tree questionnaire that recommends a career path based on user answers."
                },
                "Intermediate": {
                    "focus": "Refactoring conditionals, pattern matching in switch statements.",
                    "task": "Learn how switch statements optimize to tableswitch/lookupswitch, and use modern switch expressions.",
                    "practice": "Refactor a multi-layered nested if-else structure into clean switch expressions."
                },
                "Advanced": {
                    "focus": "Optimizing conditional evaluation, branch prediction, and state machines.",
                    "task": "Study processor branch prediction and how layout of conditionals affects execution speed.",
                    "practice": "Implement a high-performance parser that avoids branching via state lookup tables."
                }
            }
        elif "loop" in lower_topic or "while" in lower_topic or "for" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Iterating over collections and repeating execution blocks.",
                    "task": "Write basic for, while, and do-while loops, and nested loops.",
                    "practice": "Generate nested loops to print geometric shapes (like pyramids) to the console."
                },
                "Intermediate": {
                    "focus": "Advanced iteration mechanisms, break/continue controls, and iterator patterns.",
                    "task": "Explore loop bounds, iterators, and using labeled breaks for multi-level exit control.",
                    "practice": "Implement a search engine that loops over a grid matrix, terminating immediately on target match."
                },
                "Advanced": {
                    "focus": "Loop unrolling, vectorization, and concurrency optimization.",
                    "task": "Study compiler loop optimizations and how loops map to hardware vector operations.",
                    "practice": "Write a parallelized loop engine using multi-threading to process large chunks of data in parallel."
                }
            }
        elif "oop" in lower_topic or "class" in lower_topic or "object" in lower_topic or "constructor" in lower_topic or "attribute" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Understanding classes, attributes, methods, and instantiating objects.",
                    "task": "Write constructors, instance fields, getters, setters, and basic helper methods.",
                    "practice": "Model a real-world entity (like a smartphone or bank card) as a class with state and behavior."
                },
                "Intermediate": {
                    "focus": "Encapsulation, access modifiers (private, protected, public), and constructor chaining.",
                    "task": "Enforce data hiding, use constructor initialization blocks, and chaining calls using this or super.",
                    "practice": "Build a secure user profile management system that encapsulates credential fields."
                },
                "Advanced": {
                    "focus": "Object layout in memory, class loading, reflection, and dynamic proxies.",
                    "task": "Analyze class metadata, and write code to inspect or modify object attributes at runtime via Reflection.",
                    "practice": "Build a custom dependency injection container that instantiates classes and injects dependencies dynamically."
                }
            }
        elif "inheritance" in lower_topic or "super" in lower_topic or "interface" in lower_topic or "polymorphism" in lower_topic or "encapsulation" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Sharing class properties and behaviors using inheritance and interfaces.",
                    "task": "Learn extends and implements keywords, and overriding base class methods.",
                    "practice": "Model a payroll system with an Employee base class and Salaried/Hourly subclasses."
                },
                "Intermediate": {
                    "focus": "Polymorphism, runtime binding, and designing clean interfaces.",
                    "task": "Design loose-coupling using interfaces, and call methods polymorphically.",
                    "practice": "Build a payment system supporting multiple processors (CreditCard, PayPal) via a common interface."
                },
                "Advanced": {
                    "focus": "Composition vs Inheritance, multiple inheritance resolutions, and API design.",
                    "task": "Analyze why composition is preferred over inheritance, and implement delegation patterns.",
                    "practice": "Refactor a deep, brittle inheritance hierarchy into a flexible component-based architecture."
                }
            }
        elif "list" in lower_topic or "array" in lower_topic or "set" in lower_topic or "map" in lower_topic or "collection" in lower_topic or "dictionary" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Storing collections of data in Arrays, Lists, Sets, or Maps.",
                    "task": "Learn syntax for list creation, adding, removing, and iterating elements.",
                    "practice": "Build a shopping cart system that tracks items, quantities, and prices."
                },
                "Intermediate": {
                    "focus": "Choosing the right collection type, sorting, and time complexity differences.",
                    "task": "Compare performance of ArrayList vs LinkedList and HashSet vs TreeSet.",
                    "practice": "Write a log dedup utility that uses a Set for unique entries and a Map to count frequencies."
                },
                "Advanced": {
                    "focus": "Internal data structure layouts, resizing factors, hash collisions, and custom sorting.",
                    "task": "Analyze the load factor of hash tables and implement custom comparators.",
                    "practice": "Build a custom thread-safe collection from scratch utilizing locking mechanism protocols."
                }
            }
        elif "string" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Manipulating text, substring searches, and simple formatting.",
                    "task": "Learn string concatenation, length, slice, and case transformations.",
                    "practice": "Write a palindrome checker and a word count utility."
                },
                "Intermediate": {
                    "focus": "String immutability and memory optimizations (String Pool, StringBuilder).",
                    "task": "Study why strings are immutable and compare performance of concatenations in loops.",
                    "practice": "Write an HTML generator that joins thousands of lines using StringBuilder/join to optimize memory."
                },
                "Advanced": {
                    "focus": "Pattern matching, regex engine compilation, and parsing algorithms.",
                    "task": "Study finite state automata in regular expressions and prevent ReDoS (Regex Denial of Service) vulnerabilities.",
                    "practice": "Build an AST token parser that parses basic arithmetic expressions from strings."
                }
            }
        elif "file" in lower_topic or "io" in lower_topic or "json" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Reading from and writing to local files.",
                    "task": "Learn basic file readers, writers, path resolution, and error cleanup.",
                    "practice": "Create a daily diary script that saves user notes to a dated file."
                },
                "Intermediate": {
                    "focus": "Structured data serialization (JSON/CSV) and file buffering.",
                    "task": "Read and write JSON schemas, configure buffered streams, and handle character encodings.",
                    "practice": "Build a task manager that preserves tasks to a structured JSON database."
                },
                "Advanced": {
                    "focus": "Asynchronous/non-blocking I/O (NIO), channels, and file locking.",
                    "task": "Study Selector models, virtual file channels, and file system watcher services.",
                    "practice": "Build a folder watcher service that triggers notifications whenever a file is created or modified."
                }
            }
        elif "exception" in lower_topic or "try" in lower_topic or "catch" in lower_topic or "error" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Gracefully handling common runtime exceptions.",
                    "task": "Learn basic try-catch/except blocks, and printing stack trace messages.",
                    "practice": "Write a division calculator that catches division-by-zero errors and invalid input strings."
                },
                "Intermediate": {
                    "focus": "Checked vs unchecked exceptions, custom exception classes, and resource management.",
                    "task": "Define custom application-specific exceptions and use try-with-resources or try-finally blocks.",
                    "practice": "Build a transaction processor that rolls back changes if a custom business validation fails."
                },
                "Advanced": {
                    "focus": "Global exception handlers, logging architecture, and error recovery policies.",
                    "task": "Configure global uncaught exception handlers and construct automated crash reports.",
                    "practice": "Build a resilient service wrapper that monitors failure rates and trips a circuit breaker."
                }
            }
        elif "thread" in lower_topic or "concurrency" in lower_topic or "parallel" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Executing code in parallel using threads.",
                    "task": "Learn basic thread creation, starting threads, and sleep/join mechanisms.",
                    "practice": "Write a countdown timer that runs on a separate thread without blocking the main CLI menu."
                },
                "Intermediate": {
                    "focus": "Thread synchronization, race conditions, and shared resources.",
                    "task": "Use locks, synchronized blocks, and atomic variables to prevent data corruption.",
                    "practice": "Build a bank transfer simulator where multiple threads concurrently move funds between accounts safely."
                },
                "Advanced": {
                    "focus": "Thread pools, Executor services, and lock-free concurrency structures.",
                    "task": "Study thread pool configuration, future/promise patterns, and memory barriers.",
                    "practice": "Build a custom worker pool that processes a queue of image conversion tasks using optimal threads."
                }
            }
        elif "complexity" in lower_topic or "big-o" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Introduction to algorithm runtime measurement and Big-O notation.",
                    "task": "Study constant O(1), linear O(n), and quadratic O(n^2) time complexities.",
                    "practice": "Write simple loops and nested loops, and analyze their execution time on varying input sizes."
                },
                "Intermediate": {
                    "focus": "Space complexity, logarithmic O(log n), and linearithmic O(n log n) complexities.",
                    "task": "Learn recursive call stack space usage, and measure memory overhead of algorithms.",
                    "practice": "Implement iterative and recursive binary search and analyze their space/time profiles."
                },
                "Advanced": {
                    "focus": "Amortized analysis, NP-complete boundaries, and recurrence relations.",
                    "task": "Study Master Theorem for divide-and-conquer recurrences and analyze dynamic arrays resizing.",
                    "practice": "Implement and write a benchmark report for three sorting algorithms under different memory profiles."
                }
            }
        elif "search" in lower_topic or "sort" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Finding and ordering elements in a collection.",
                    "task": "Learn Linear Search and basic O(n^2) sorting like Bubble Sort or Selection Sort.",
                    "practice": "Write Bubble Sort and Linear Search from scratch, testing them with unsorted lists."
                },
                "Intermediate": {
                    "focus": "Divide-and-conquer sorting and logarithmic search algorithms.",
                    "task": "Implement Binary Search, Quick Sort, and Merge Sort, comparing execution counts.",
                    "practice": "Create a database record finder that sorts records by ID using Merge Sort and finds them via Binary Search."
                },
                "Advanced": {
                    "focus": "Hybrid sorting algorithms (Timsort), stability, and external sorting.",
                    "task": "Study in-place sorting optimizations and how Java/Python implement standard sorting.",
                    "practice": "Write an external merge sort utility that can sort a 10GB file on a machine with 512MB RAM."
                }
            }
        elif "tree" in lower_topic or "bst" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Hierarchical data representation using binary trees.",
                    "task": "Define tree nodes and understand left/right child relationships.",
                    "practice": "Build a Binary Tree structure and write methods to insert nodes."
                },
                "Intermediate": {
                    "focus": "Tree traversals (inorder, preorder, postorder) and Binary Search Trees (BST).",
                    "task": "Implement recursive and iterative BST insertion, search, and deletion.",
                    "practice": "Write a validation script that checks if a given binary tree is a valid BST."
                },
                "Advanced": {
                    "focus": "Self-balancing trees (AVL, Red-Black Trees) and multi-way trees (B-Trees).",
                    "task": "Study rotation rules in AVL trees or node splitting in B-Trees.",
                    "practice": "Implement a self-balancing AVL Tree supporting node insertion and rotation balancing."
                }
            }
        elif "graph" in lower_topic or "bfs" in lower_topic or "dfs" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Modeling networks using graphs.",
                    "task": "Learn vertex/edge concepts, adjacency matrix, and adjacency list representations.",
                    "practice": "Create an adjacency list graph representation of a social network."
                },
                "Intermediate": {
                    "focus": "Graph traversal algorithms: Breadth-First Search (BFS) and Depth-First Search (DFS).",
                    "task": "Implement BFS and DFS using queues and recursion/stacks.",
                    "practice": "Write a pathfinder that finds the shortest path in an unweighted grid maze using BFS."
                },
                "Advanced": {
                    "focus": "Weighted graphs and pathfinding optimization algorithms (Dijkstra, A*).",
                    "task": "Study shortest path relaxations, priority queues in Dijkstra, and heuristics in A*.",
                    "practice": "Implement Dijkstra's algorithm to find the fastest routing path on a weighted city map."
                }
            }
        elif "dynamic programming" in lower_topic or "dp" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Introduction to overlapping subproblems and memoization.",
                    "task": "Study Fibonacci sequence using naive recursion vs memoization (top-down DP).",
                    "practice": "Write a memoized Fibonacci calculator and measure the speed-up factor."
                },
                "Intermediate": {
                    "focus": "Tabulation (bottom-up DP) and 1D/2D state transitions.",
                    "task": "Compare memoization vs tabulation and learn the Coin Change or Grid Traveler problem.",
                    "practice": "Build a Coin Change solver that calculates the minimum coins required for a target sum."
                },
                "Advanced": {
                    "focus": "State compression, multi-dimensional DP, and Knapsack problems.",
                    "task": "Analyze 0-1 Knapsack and Longest Common Subsequence (LCS) problems, optimizing space complexity.",
                    "practice": "Implement a 0-1 Knapsack solver that optimizes space by reusing a single array row."
                }
            }
        elif "regression" in lower_topic or "ml" in lower_topic or "machine learning" in lower_topic or "statistics" in lower_topic or "data analysis" in lower_topic or "linear algebra" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "Foundational math and data concepts for Machine Learning.",
                    "task": "Learn matrix operations, vector math, basic probability, and linear regressions.",
                    "practice": "Write a simple linear regression model from scratch using ordinary least squares math."
                },
                "Intermediate": {
                    "focus": "Supervised algorithms, data cleaning, and model evaluations.",
                    "task": "Learn Decision Trees, Random Forests, train-test splitting, and feature scaling.",
                    "practice": "Use Scikit-Learn to clean a dataset, train a classifier, and print precision/recall metrics."
                },
                "Advanced": {
                    "focus": "Neural network architectures, optimizer mathematics, and deep learning.",
                    "task": "Study backpropagation calculus, gradient descent optimizations, and loss functions.",
                    "practice": "Build a neural network node layer from scratch using raw matrix multiplication in NumPy."
                }
            }
        elif "rest api" in lower_topic or "fastapi" in lower_topic or "http" in lower_topic:
            matched_details = {
                "Beginner": {
                    "focus": "HTTP request-response cycle and building simple REST endpoints.",
                    "task": "Learn HTTP methods (GET, POST, PUT, DELETE), status codes, and routing.",
                    "practice": "Build a basic API endpoint that returns message responses for path parameters."
                },
                "Intermediate": {
                    "focus": "Request validation, query filters, and data persistence integration.",
                    "task": "Implement Pydantic model validations, query parameter parsers, and mock DB states.",
                    "practice": "Create a secure CRUD API that saves data records and validates input fields."
                },
                "Advanced": {
                    "focus": "API authentication mechanisms, rate limiting, and performance tuning.",
                    "task": "Study OAuth2, JWT verification, CORS headers, and asynchronous event loops.",
                    "practice": "Build a secure FastAPI app with token authorization, route protections, and request rate-limiting rules."
                }
            }

        if matched_details and skill_level in matched_details:
            return matched_details[skill_level]

        # Dynamic fallback generator for custom/unrecognized topics
        focus_templates = {
            "Beginner": f"Learning core concepts, syntax rules, and fundamentals of '{clean_topic}'.",
            "Intermediate": f"Studying best practices, structures, and common design patterns for '{clean_topic}'.",
            "Advanced": f"Optimizing performance, exploring internals, and managing edge cases for '{clean_topic}'."
        }
        
        task_templates = {
            "Beginner": f"Research basic syntax, read official documentation, and write code examples for {clean_topic}.",
            "Intermediate": f"Refactor standard structures, handle exceptions, and implement unit tests for {clean_topic}.",
            "Advanced": f"Analyze memory/performance constraints, study security issues, and design extensible architecture for {clean_topic}."
        }
        
        practice_templates = {
            "Beginner": f"Build a simple console script allocating {daily_hours} hours to experiment with basic properties of {clean_topic}.",
            "Intermediate": f"Create a modular project implementing custom validation rules and error-handling schemes for {clean_topic}.",
            "Advanced": f"Develop a production-ready component featuring concurrent processing or advanced optimization for {clean_topic}."
        }
        
        return {
            "focus": focus_templates.get(skill_level, focus_templates["Beginner"]),
            "task": task_templates.get(skill_level, task_templates["Beginner"]),
            "practice": practice_templates.get(skill_level, practice_templates["Beginner"])
        }

    def _generate_plan_offline(self, topic: str, duration_weeks: int, daily_hours: float, skill_level: str) -> str:
        """
        Generates a highly personalized day-by-day study plan programmatically.
        Acts as the offline engine, respecting topic, level, weeks, and hours.
        """
        total_days = duration_weeks * 7
        total_hours = total_days * daily_hours
        
        # Sub-topic list definitions based on topic mapping
        topic_lower = topic.lower()
        
        # Predefined topics with 4 major phases/modules
        python_curriculum = [
            ("Python Core Basics & Syntax", ["Variables & Data Types", "Operators & Basic Math", "Control Flow: If-Else", "Loops: For & While", "Loop Control (Break, Continue)", "String Methods & Formatting", "Week 1 Review & Core Syntax Check"]),
            ("Data Structures & Modules", ["Working with Lists", "Tuples & Sets", "Dictionaries & Key-Value pairs", "Custom Functions & Scope", "Built-in Functions & Modules", "Error & Exception handling (Try/Except)", "Mini Command-line Project"]),
            ("Object-Oriented Programming (OOP)", ["Classes & Objects", "Attributes & Custom Methods", "Constructor (__init__)", "Inheritance & Subclasses", "Method Overriding", "Polymorphism & Encapsulation", "Building an OOP CLI App"]),
            ("File Operations & Web APIs", ["Reading Text Files", "Writing & Appending Data", "Working with JSON Files", "Introduction to Package Managers (pip)", "Making HTTP requests", "Building REST APIs with FastAPI", "Final Capstone Project Refinement"])
        ]
        
        java_curriculum = [
            ("Java Basics & Primitive Types", ["Java Virtual Machine & Setup", "Variables & Primitive Types", "Arithmetic Operators", "Boolean logic & If Statements", "Switch Statements", "While & Do-While Loops", "For Loops & Nested Loops"]),
            ("Classes & OOP Foundations", ["Declaring Classes & Creating Objects", "Defining Methods & Parameters", "Constructors & Overloading", "Access Modifiers (public/private)", "Inheritance & Super Keyword", "Interfaces & Abstract Classes", "OOP Library Management Project"]),
            ("Java Collections & Strings", ["String Manipulation & Builder", "Java Arrays", "ArrayList & Lists", "HashSet & Sets", "HashMap & Dictionary maps", "Wrapper Classes & Autoboxing", "Collections Review & Sorting"]),
            ("Exceptions, I/O & Advanced Java", ["Try-Catch Block Exceptions", "Finally Block & Resource Closing", "Java File I/O (FileReader/Writer)", "Basic Threads & Concurrency", "Java Streams API", "Lambda Expressions", "Final Java Database CLI Project"])
        ]
        
        data_structures_curriculum = [
            ("Foundations & Array Lists", ["Introduction to Big-O Notation", "Time & Space Complexity", "Static & Dynamic Arrays", "Two-Pointer Problems", "Stacks: LIFO Concept & Code", "Queues: FIFO Concept & Code", "Singly Linked List Implementation"]),
            ("Linked Lists & Searching", ["Doubly Linked Lists", "Recursion & Call Stacks", "Binary Search Algorithm", "Sorting: Bubble & Insertion Sort", "Sorting: Merge Sort", "Sorting: Quick Sort", "Practice LeetCode Arrays/Strings"]),
            ("Trees, Hash Tables & Graphs", ["Binary Trees & Node traversals", "Binary Search Trees (BST)", "Hash Table Collision Resolution", "Introduction to Graph Nodes", "Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Graph Traversals Exercises"]),
            ("Advanced Structures & Algorithms", ["Heaps & Priority Queues", "Trie (Prefix Tree)", "Dynamic Programming: Recursion + Memoization", "DP: Tabulation", "Greedy Algorithms", "Sliding Window algorithms", "Final Mock Interview Review"])
        ]
        
        ml_curriculum = [
            ("Math Foundations & Data Analysis", ["Linear Algebra (Vectors/Matrices)", "Statistics & Probability basics", "NumPy arrays & Vectorization", "Pandas: DataFrames & Series", "Data Cleaning & Imputation", "Data Visualization (Matplotlib)", "Exploratory Data Analysis (EDA)"]),
            ("Supervised Learning (Regression/Classify)", ["Linear Regression concepts", "Gradient Descent Optimization", "Logistic Regression for classification", "Decision Trees & Splitting metrics", "Random Forests & Ensemble basics", "K-Nearest Neighbors (KNN)", "Model Fitting exercises"]),
            ("Unsupervised Learning & Evaluation", ["K-Means Clustering", "Principal Component Analysis (PCA)", "Model evaluation: Precision/Recall/F1", "ROC & AUC curves", "Train-Test Split & Overfitting", "Cross-Validation techniques", "Hyperparameter Tuning"]),
            ("Neural Networks & Deployment", ["Perceptron & Activation Functions", "Multi-Layer Perceptron (MLP)", "Introduction to TensorFlow/PyTorch", "Building a Simple Neural Net", "Model Serialization (Pickle/Joblib)", "Deploying ML Models (FastAPI)", "Final Project Presentation"])
        ]
        
        generic_curriculum = [
            (f"{topic} Core Foundations", ["Core terminology & vocabulary", "Setting up development environment", "Basic syntax and structure", "Variables and core configurations", "Interactive exercises", "Debugging basic code", "Phase 1 Knowledge Assessment"]),
            (f"{topic} Intermediate Syntax", ["Intermediate methods & functions", "Data flow and parameters", "Handling common error scenarios", "File read/write operations", "Best practices and clean architecture", "Refactoring code examples", "Mini-application build"]),
            (f"{topic} Design Patterns", ["Advanced structures and schemas", "Object modeling and dependencies", "Performance benchmarks", "Memory management guidelines", "Third-party libraries integration", "Security and safety check", "Advanced system architecture design"]),
            (f"{topic} Application & Refinement", ["Integrating all components", "Deploying and compiling programs", "Writing integration tests", "Profiling and optimization", "User interface development", "Reviewing documentation", "Final Capstone Project Implementation"])
        ]
        
        # Pick curriculum
        curriculum = generic_curriculum
        if "python" in topic_lower:
            curriculum = python_curriculum
        elif "java" in topic_lower:
            curriculum = java_curriculum
        elif "data structure" in topic_lower or "algorithm" in topic_lower:
            curriculum = data_structures_curriculum
        elif "machine learning" in topic_lower or "ml" in topic_lower or "data science" in topic_lower:
            curriculum = ml_curriculum
            
        plan_md = []
        plan_md.append(f"# 📅 Study Schedule: {topic}")
        plan_md.append(f"**Target Level**: {skill_level} | **Duration**: {duration_weeks} Weeks ({total_days} Days) | **Daily Commitment**: {daily_hours} hrs/day (~{total_hours:.1f} total hours)\n")
        plan_md.append("---")
        
        day_counter = 1
        for week in range(1, duration_weeks + 1):
            # Select module (loop around if weeks > 4)
            module_idx = (week - 1) % 4
            module_name, daily_topics = curriculum[module_idx]
            
            plan_md.append(f"## 📌 Week {week}: {module_name}")
            plan_md.append(f"*Target Milestone: Complete core topics of {module_name} and pass self-evaluation.*")
            
            for day in range(1, 8):
                if day_counter > total_days:
                    break
                topic_idx = (day - 1) % len(daily_topics)
                daily_topic = daily_topics[topic_idx]
                
                # Contextual task adjustments based on Level and Hours via lookup helper
                details = self._get_topic_details(daily_topic, skill_level, daily_hours)
                plan_md.append(f"\n### Day {day_counter}: {daily_topic}")
                plan_md.append(f"- **Focus**: {details['focus']} (Allocated: {daily_hours} hrs)")
                plan_md.append(f"- **Task**: {details['task']}")
                plan_md.append(f"- **Practice**: {details['practice']}")
                
                day_counter += 1
                
            # Weekly Milestone
            milestone_description = f"Successfully write a 1-page summary explaining the concepts of {module_name} in simple terms and build a minor test application."
            if skill_level == "Intermediate":
                milestone_description = f"Implement a complete module using {module_name} standards, including code comments and a solid test suite."
            elif skill_level == "Advanced":
                milestone_description = f"Build and profile a high-performance script using {module_name} concepts, explaining memory leaks or speed bottlenecks."
                
            plan_md.append(f"\n🏆 **Week {week} Milestone:** {milestone_description}")
            plan_md.append("\n" + "-" * 40)
            
        # Resources section
        plan_md.append("### 📚 Recommended Real Learning Resources:")
        if "python" in topic_lower:
            plan_md.append("1. **Official Python Docs**: [docs.python.org](https://docs.python.org/3/) - The absolute gold standard.")
            plan_md.append("2. **Real Python**: [realpython.com](https://realpython.com/) - High-quality, practical Python tutorials.")
            plan_md.append("3. **StudyPilot AI Quizzes**: Take Python practice quizzes in the Quiz tab.")
        elif "java" in topic_lower:
            plan_md.append("1. **Oracle Java Documentation**: [docs.oracle.com/en/java](https://docs.oracle.com/en/java/) - Standard API specs.")
            plan_md.append("2. **Baeldung**: [baeldung.com](https://www.baeldung.com/) - Excellent intermediate/advanced Java guides.")
            plan_md.append("3. **StudyPilot AI**: Generate Java quizzes locally to check class relationships.")
        elif "data structure" in topic_lower or "algorithm" in topic_lower:
            plan_md.append("1. **GeeksforGeeks DS/ALGO**: [geeksforgeeks.org](https://www.geeksforgeeks.org/) - Structured reference.")
            plan_md.append("2. **Visualgo**: [visualgo.net](https://visualgo.net/en) - Interactive algorithm visualizations.")
            plan_md.append("3. **StudyPilot AI Planner**: Review daily check-boxes regularly to measure growth.")
        elif "machine learning" in topic_lower or "ml" in topic_lower or "data science" in topic_lower:
            plan_md.append("1. **Scikit-Learn User Guide**: [scikit-learn.org](https://scikit-learn.org/) - Clear explanations of classic ML.")
            plan_md.append("2. **Kaggle Learn**: [kaggle.com/learn](https://www.kaggle.com/learn) - Interactive micro-courses.")
            plan_md.append("3. **StudyPilot AI**: Upload ML study notes in the Notes tab to extract summaries.")
        else:
            plan_md.append(f"1. **Official Guide**: Refer to official documentation for {topic}.")
            plan_md.append("2. **MDN Web Docs / DevDocs**: High-quality references for languages and frameworks.")
            plan_md.append("3. **Active Recall**: Test yourself regularly using our local Quiz Generator tab.")
            
        full_plan = "\n".join(plan_md)
        return self.clean_html_entities(full_plan)

    def _execute_simulation(self, prompt: str, session_state: SessionState) -> str:
        topic = session_state.get("planner_topic", "General Subject")
        weeks = session_state.get("planner_weeks", 4)
        hours = session_state.get("planner_hours", 2.0)
        level = session_state.get("planner_level", "Beginner")
        return self.generate_plan(topic, weeks, hours, level)

