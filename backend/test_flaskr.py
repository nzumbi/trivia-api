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
        self.database_name = "trivia"
        self.DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
        self.DB_USER = os.getenv('DB_USER', 'student')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'student')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia')
        self.database_path = "postgres://{}:{}@{}/{}".format(
            self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)


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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories_all(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_categories_invalid(self):
        res = self.client().delete('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)



    def test_get_create_pages(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_get_quations_without_pages(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    


    def test_question_delete(self):
        question = Question.query.order_by(self.db.desc(Question.id)).first()
        self.assertNotEqual(question, None)
        id =question.id
        res = self.client().delete('/questions/'+str(id))
        data = json.loads(res.data)
        question = Question.query.get(id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
        self.assertEqual(question, None)



    def test_question_delete_question_out_of_rage(self):
        res = self.client().delete('/questions/4000')
        data = json.loads(res.data)

    def test_adding_new_question(self):
        question_new = {
            'question': 'what is the highest mountain in kenya?',
            'answer': 'mt kenya',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=question_new)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_adding_question_sent_422(self):
        res = self.client().post('/questions/6000',)
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)

    def test_question_search_by_term(self):
        res = self.client().post('/search', json={"searchTerm":"What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])


    def test_question_search_by_term_not_successful(self):
        res = self.client().post('/questions/search', json={"search": "ribashogirogasheshiakili"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'requested resource not found')



    def test_pages_out_of_rage_return_404(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "requested resource not found")





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()