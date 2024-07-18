import hashlib
import json
import random,string
from time import time
from textwrap import dedent
from flask import Flask, jsonify, request, redirect, render_template, url_for, flash
import requests
from uuid import uuid4
from urllib.parse import urlparse
from flask_mongoengine import MongoEngine
from config import Config

# ***************************************************************************
# ~~~~~~~~~~~~~~~~~~~~~~~~~CLASS FOR CREATING BLOCKCHAIN~~~~~~~~~~~~~~~~~~~~~
# ***************************************************************************

# methods inside block chain class
class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(proof=100,previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, patient, illness, tests, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param patient: <str> Address of the Sender
        :param illness: <str> Address of the Recipient
        :param tests: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'patient': patient,
            'illness': illness,
            'tests': tests,
            'amount': amount
        })

        return self.last_block['index']+1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True


    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

# Instantiate our Node
app = Flask(__name__)
app.config.from_object(Config)
db = MongoEngine(app)

def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['to_pretty_json'] = to_pretty_json

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# ***************************************************************************
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~DATABASE MODELS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ***************************************************************************

# Database Model class for storing Personal info of Patients
class PatientInfo(db.Document):
    patient_id = db.StringField(primary_key=True)
    name = db.StringField(required=True, max_length=200)
    date_of_birth = db.DateTimeField(required=True)
    address = db.StringField(required=True)
    city = db.StringField(required=True)

# Database Model class for storing Personal info of Patients
class PatientRecordsList(db.Document):
    patient_id = db.StringField(primary_key=True)
    medical_record_block_ids = db.ListField(db.IntField(max_length=30))

# ***************************************************************************
# ~~~~~~~~~~~~~~~~~~~~~~FORM CLASSES FOR FLASK APP~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ***************************************************************************
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class PatientRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth (YYYY-MM-DD)', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PatientMedicalRecordForm(FlaskForm):
    patient_id = StringField('Patient Id', validators=[DataRequired()])
    illness = StringField('Illness', validators=[DataRequired()])
    medical_tests = StringField('Medical Tests')
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NodeRegistrationForm(FlaskForm):
    nodes = StringField('Node Address (http://0.0.0.0:5000)', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RecordRetrievalForm(FlaskForm):
    patient_id = StringField('Patient ID', validators=[DataRequired()])
    submit = SubmitField('Submit')
# ***************************************************************************
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ROUTES FOR FLASK APP~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ***************************************************************************

#methods to access blockchain using client-server mechanism
@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.


    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    text = json.dumps(response, indent = 4, separators = (',', ': '))
    return render_template("common.html", text=text)

@app.route('/transactions/new', methods=['GET', 'POST'])
def new_transaction1():
    form = PatientMedicalRecordForm()
    if form.validate_on_submit():
        values = request.form.to_dict()
        # values = request.get_json()
        # print("VALUES",values)
        # Check that the required fields are in the POST'ed data

        # required = ['patient_id','illness','medical_tests','amount']
        # if not all(k in values for k in required):
        #     return 'Missing values', 400

        # Create a new Transaction
        index = blockchain.new_transaction(values['patient_id'], values['illness'], values['medical_tests'], int(values['amount']))
        
        # Storing medical record block no to corresponding patient database
        patient_record = PatientRecordsList.objects(patient_id = values['patient_id']).get()
        patient_record.medical_record_block_ids.append(index)
        patient_record.save()

        response = {'message': f'Transaction will be added to Block {index}'}
        text = json.dumps(response, indent = 4, separators = (',', ': '))
        return render_template("common.html", text=text)
    return render_template('add_transaction.html', form=form)

# Method for retrieval of Past Medical Reocords of patients
@app.route('/retrieve', methods=['GET', 'POST'])
def info_retrieval():
    response1 = dict()
    form = RecordRetrievalForm()
    if form.validate_on_submit():
        values = request.form.to_dict()
        k = PatientRecordsList.objects(patient_id = values['patient_id']).get()
        # print("kkkk",k.patient_id, k.medical_record_block_ids)
        
        for d in k.medical_record_block_ids: # iterate through block indexes
            for l in blockchain.chain:
                if d==l['index']:
                    for f in l['transactions']:
                        if f['patient']==values['patient_id']:
                            response1.setdefault('info', []).append({"illness": f['illness'], "tests": f['tests']})  #to create dictionary appending multiple illness
        text = json.dumps(response1, indent=4, separators=(',', ': '))
        return render_template("common.html", text=text)
    return render_template("info_retrieval.html", form=form)

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    text = json.dumps(response, indent = 4, separators = (',', ': '))
    return render_template("common.html", text=text)

@app.route('/nodes/register', methods=['GET', 'POST'])
def register_nodes():
    form = NodeRegistrationForm()
    if form.validate_on_submit():
        # values = request.get_json()
        values = request.form.to_dict()
        nodes = [values.get('nodes')]
        # print(nodes)
        if nodes is None:
            return "Error: Please supply a valid list of nodes", 400

        for node in nodes:
            blockchain.register_node(node)

        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes),
        }
        text = json.dumps(response, indent = 4, separators = (',', ': '))
        return render_template("common.html", text=text)
    return render_template('register_nodes.html', form=form)

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    text = json.dumps(response, indent = 4, separators = (',', ': '))
    return render_template("common.html", text=text)

@app.route('/')
def home():
    return render_template('home.html')

def generate_unique_16char_id():
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    # print(x)
    return x

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        new_patient_id =  generate_unique_16char_id()
        new_patient = PatientInfo(patient_id=new_patient_id, name=form.name.data, date_of_birth=form.date_of_birth.data, address=form.address.data, city=form.city.data)
        new_patient.save()
        new_patient_records_list = PatientRecordsList(patient_id=new_patient_id)
        new_patient_records_list.save()
        flash("Patient is Registered Successfully", "success")
        return redirect(url_for('home'))
    return render_template('register_patient.html', form= form)


# main() method to host a local server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    