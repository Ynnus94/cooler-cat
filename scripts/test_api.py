import unittest
import os
import shutil
import json
import io
from server import app, JOBS_DIR

class TestCoolerCatAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a dummy XLF file for testing (XLIFF 2.0 format)
        self.test_xlf_content = """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
    <unit id="u1">
      <segment>
        <source>Hello world</source>
        <target>Bonjour le monde</target>
      </segment>
    </unit>
    <unit id="u2">
      <segment>
        <source>I cannot do this</source>
        <target>Je peuvent être ajoutés faire cela</target>
      </segment>
    </unit>
  </file>
</xliff>"""
        self.test_filename = 'test_job.xlf'
        
    def tearDown(self):
        # Clean up jobs directory after tests
        pass

    def test_1_create_job(self):
        """Test job creation endpoint"""
        data = {
            'file': (io.BytesIO(self.test_xlf_content.encode('utf-8')), self.test_filename)
        }
        response = self.app.post('/api/jobs', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('job_id', data)
        self.job_id = data['job_id']
        return self.job_id

    def test_2_list_jobs(self):
        """Test listing jobs"""
        # Create a job first
        job_id = self.test_1_create_job()
        
        response = self.app.get('/api/jobs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        
        # Verify our job is in the list
        found = False
        for job in data:
            if job['id'] == job_id:
                found = True
                break
        self.assertTrue(found)

    def test_3_get_job_details(self):
        """Test getting job details"""
        job_id = self.test_1_create_job()
        
        response = self.app.get(f'/api/jobs/{job_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], job_id)
        self.assertTrue(data['has_csv'])

    def test_4_ai_revision(self):
        """Test AI revision endpoint"""
        job_id = self.test_1_create_job()
        
        # Save original key if present
        original_key = os.environ.get('GEMINI_API_KEY')
        # Set to empty string to prevent load_dotenv from reading .env
        os.environ['GEMINI_API_KEY'] = ""
            
        try:
            response = self.app.post(f'/api/jobs/{job_id}/revise', json={})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('stats', data)
            self.assertIn('revised', data['stats'])
            
            # Verify data contains AI revision and confidence score
            data_response = self.app.get(f'/api/jobs/{job_id}/data')
            rows = json.loads(data_response.data)['data']
            
            # Check the second row (which had an error in our test content)
            # "Je peuvent être ajoutés faire cela" -> should be corrected by mock logic
            found_revision = False
            for row in rows:
                if row.get('AI Revision'):
                    found_revision = True
                    self.assertIn('Confidence Score', row)
                    # Verify mock logic worked (it sets confidence to 50)
                    self.assertEqual(row.get('Confidence Score'), '50')
                    break
            self.assertTrue(found_revision)
        finally:
            # Restore key
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key

    def test_5_progress_endpoint(self):
        """Test progress endpoint"""
        job_id = self.test_1_create_job()
        
        # Path to progress file
        # In test_1_create_job, we see jobs are created in 'jobs' dir relative to cwd
        job_dir = os.path.join('jobs', job_id)
        progress_file = os.path.join(job_dir, 'progress.json')
        
        # 1. Test default state (no file)
        response = self.app.get(f'/api/jobs/{job_id}/progress')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['percentage'], 0)
        self.assertEqual(data['status'], 'unknown')
        
        # 2. Create progress file
        test_progress = {
            'current': 5,
            'total': 10,
            'percentage': 50,
            'message': 'Halfway there!',
            'status': 'processing'
        }
        with open(progress_file, 'w') as f:
            json.dump(test_progress, f)
            
        # 3. Test with file
        response = self.app.get(f'/api/jobs/{job_id}/progress')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['percentage'], 50)
        self.assertEqual(data['message'], 'Halfway there!')
        
        # Cleanup
        if os.path.exists(progress_file):
            os.remove(progress_file)

if __name__ == '__main__':
    unittest.main()
