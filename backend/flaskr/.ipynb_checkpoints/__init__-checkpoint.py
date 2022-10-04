#from msilib.schema import Patch
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_pages(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    currentQuestions = questions[start:end]

    return currentQuestions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow

    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories',methods=['GET'])
    def get_categories_all():
        categories = Category.query.all()
        categorydict= {}

        for category in categories:
            categorydict[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categorydict
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions',methods=['GET'])
    def get_all_questions():

            selection = Question.query.order_by(Question.id).all()
            currentQuestions = create_pages(request, selection)
            totalQuestions = len(selection)

            if (len(currentQuestions) == 0):
                abort(404)

            categories = Category.query.all()
            categoriesdict = {}
            for category in categories:
                categoriesdict[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': totalQuestions,
                'categories': categoriesdict
            })
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def question_delete_by_question_id(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()


            if question is None:
                abort(404)

            question.delete()


            selection = Question.query.order_by(Question.id).all()
            currentQuestions = create_pages(request, selection)

            return jsonify({
                'success': True,
            })

        except Exception as e:
            print(e)
            abort(404)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=['POST'])
    def adding_new_question():
        body = request.get_json()
        question_new = body.get('question', None)
        answer_new = body.get('answer', None)
        category_new = body.get('category', None)
        new_difficult_level = body.get('difficulty', None)

        try:
            question = Question(question=question_new, answer=answer_new,
                                category=category_new, difficulty=new_difficult_level)
            question.insert()


            selection = Question.query.order_by(Question.id).all()
            currentQuestions = create_pages(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': currentQuestions,
                'total_questions': len(selection)
            })

        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/search", methods=['POST'])
    def question_search_by_term():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if questions:
            currentQuestions = create_pages(request, questions)
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })
        else:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions")
    def questions_based_on__category(id):
        #category = Category.query.filter_by(id=id).one_or_none()
        #if category:
        try:
    
            selection = Question.query.filter_by(category=str(id)).all()
            currentQuestions = create_pages(request, selection)

            categories = Category.query.all()
            categoriesdict = {}
            for category in categories:
                categoriesdict[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'categories': categoriesdict
            })
        except Exception as e:
            print(e)
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and  question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    

    @app.route('/quizzes', methods=['POST'])
    def play_trivia_quiz():
        body = request.get_json()
        quizCategory = body.get('quiz_category')

        trivia_id = quizCategory['id']
        previous_questions = body.get('previous_questions')

        try:
            if trivia_id == 0:
                
                current_page = Question.query.filter(Question.id.notin_(previous_questions),
                Question.category == trivia_id).all()

            else:
                current_page = Question.query.filter(Question.id.notin_(previous_questions),

                Question.category == trivia_id).all()

            question = None
            if(current_page):
                next_page = random.choice(current_page)

            return jsonify({
                'success': True,
                'question': next_page.format()
            })
            

        except Exception as e:
            print(e)
            abort(404)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def requested_resource_not_found(error):
        return( 
            jsonify({'success': False, 'error': 404,'message': 'requested resource not found'}),
            404
        )

    @app.errorhandler(422)
    def request_not_processed(error):
        return(
            jsonify({'success': False, 'error': 422,'message': 'provided instructions cannot be processed'}),
            422

        )

    @app.errorhandler(405)
    def method_not_valid(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "requested method is not valid!"
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "client error, make modifications to request!"
        }), 400
    return app
