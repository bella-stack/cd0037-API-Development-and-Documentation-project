import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def afterRequest(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    endpoint to handle GET requests for all available categories.
    """
    @app.route("/categories")
    def getCategories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)
        result = {}
        for category in categories:
            result[category.id] = category.type
        
        return jsonify({'categories': result})


    """
    endpoint to handle GET requests for questions,
    """
    @app.route("/questions")
    def getQuestions():
        items_limit = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
        page = request.args.get("pages", 1, type=int)
        current_index = page - 1
        start_page = (page - 1) * QUESTIONS_PER_PAGE
        end_page = start_page + QUESTIONS_PER_PAGE
        questions = Question.query.order_by(
                Question.id
            ).limit(items_limit).offset(current_index * items_limit).all()
        formatted_questions = [ question.format() for question in questions ]
        categories = Category.query.all()
        cat_result = {}
        for category in categories:
            cat_result[category.id] = category.type
        if len(formatted_questions[start_page:end_page]) == 0:
            abort(404)
            
        result = {
            "questions": formatted_questions,
            "total_questions": len(questions),
            "current_category": "",
            "categories": cat_result
        }
        return jsonify(result)

    """
    endpoint to DELETE question using a question ID.
    """
    @app.route("/questions/<int:id>", methods=["DELETE"])
    def deleteQuestion(id):
        try:
            question = Question.query.filter(Question.id == id).first()
            question.delete()
            questions = Question.query.all()
            formatted_questions = [
                question.format() for question in questions
                ]
            return jsonify({"questions": formatted_questions})
        except Exception:
            abort(500)

    """
    endpoint to POST a new question
    """
    
    @app.route('/questions', methods=['POST'])
    def createQuestion():
        body = request.get_json()
        question = Question(
            question = body.get('question', None), 
            answer = body.get('answer', None), 
            category = body.get('category', None), 
            difficulty =body.get('difficulty', None))
        question.insert()


        return jsonify({
            "success": True,
            "created": question.id
        })
    
    

    """
    endpoint to get questions based on a search term.
    """
    @app.route('/questions/search', methods=['POST'])
    def searchQuestion():
        res = {}
        term = request.get_json()["searchTerm"]
        page = 1
        start_page = (page - 1) * QUESTIONS_PER_PAGE
        end_page = start_page + QUESTIONS_PER_PAGE
        ques_result = []
        questions = Question.query.filter(Question.question.ilike("%" + term + "%")).all()
        formatted_questions = [ question_query.format() for question_query in questions]
        categories = Category.query.all()
        
        for category in categories:
            res[category.id] = category.type
        
        result = {
            "questions": formatted_questions[start_page:end_page],
            "total_questions": len(questions),
            "current_category": "",
            "categories": res
        }
        return jsonify(result)

    """
    GET endpoint to get questions based on category.
    """
    @app.route("/categories/<int:id>/questions")
    def getQuestionsByCategory(id):
        ques_result = []
        questions = Question.query.filter(Question.category == str(id)).all()
        formatted_questions = [ question.format() for question in questions ]
        categories = Category.query.all()
        currentCategory = Category.query.filter(Category.id == id).first().type
        categoriesWithType = {}
        for category in categories:
            categoriesWithType[category.id] = category.type
        result = {
            "questions": formatted_questions,
            "total_questions": len(questions),
            "current_category": currentCategory,
            "categories": categoriesWithType
        }
    
        return jsonify(result)

    """
    POST endpoint to get questions to play the quiz.
    """
    @app.route("/quizzes", methods=["POST"])
    def quizizz():
        request_quiz = request.get_json()
        prevId = request_quiz["previous_questions"]
        category = request_quiz["quiz_category"]["id"]

        if category == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == str(category)).all()

        ids = [ question.id for question in questions ]
        resIds = list(set(ids) - set(prevId))
        if resIds == []:
            question = ""
        else:
            current = Question.query.filter(
                Question.id == int(random.choice(resIds))
                ).first()
            question = {
                "id": current.id,
                "question": current.question,
                "answer": current.answer
            }

        return jsonify({"question": question})

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

