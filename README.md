# Voting Machine
A voting machine that manages 3 different users i.e Admin, Candidate and Voter. Each with it's own set of features.
### Features
- Halka Addition(admin)
- Approve Candidates(admin)
- Set Polling Schedule(admin)
- Send Invitation(admin)
- View Total Votes(candidate)
- Voters in my Area(candidate)
- Become A Candidate(voter)
- Vote(voter)
- Candidate Profiles(voter)
### Installation
Make Virtual Environment:
```bash
pip install -m venv
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Make DB migrations:
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```