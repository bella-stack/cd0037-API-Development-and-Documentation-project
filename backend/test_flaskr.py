import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path ="postgres://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def testAddNewQuestion(self):
        res = self.client().post('/questions', json=self.new_question)
        self.assertEqual(res.status_code, 200)
        self.assertMultiLineEqual(json.loads(res.data), self.new_question['question'])

    def testDeleteQuestion(self):
        res = self.client().delete('/questions/' + str(Question.query.first().id))
        question = Question.query.filter(Question.id == 1).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()