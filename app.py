from flask import Flask, render_template,request,redirect,send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DecimalField
from wtforms.validators import DataRequired,InputRequired,NumberRange, ValidationError

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Inventory.db'
app.config['SECRET_KEY']='secret key'
db = SQLAlchemy(app)

# database model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(100), nullable=False)
    itemDescription = db.Column(db.Text, nullable=False)
    itemCount = db.Column(db.Integer, nullable=False)
    itemPrice = db.Column(db.Numeric( scale =2, asdecimal=True), nullable=False)
    itemTotalPrice = db.Column(db.Numeric( scale =2, asdecimal=True), nullable=False)
    dateOfProduce = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)

    def __repr__(self):
        return 'Inventory item' + str(self.id)

# create a Form Class
class Forms(FlaskForm):
    itemName = StringField('Item Name', validators = [DataRequired(message='hi')])
    itemDescription = TextAreaField('Item Description', validators = [DataRequired()])
    itemCount = IntegerField('Item Count', validators = [DataRequired(), NumberRange(min = 1)])
    itemPrice = DecimalField('Item Price', validators = [InputRequired(), NumberRange(min = 0)])

    '''
    def validate_itemPrice(self, itemPrice):
        x = float(self.itemPrice.data)
        if x <= 0:
            raise ValidationError('Price must be greater than 0$')
        elif len(x.rsplit('.')[-1]) > 2:
            raise ValidationError('Price is invalid. Enter a value with not more than 2 decimal places.')
    '''
    submit = SubmitField("Submit")
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/allitems/addnew',methods=['GET','POST'])
def add():
    if request.method == 'POST':
        inventory_itemName = request.form['itemName']
        inventory_itemDescription = request.form['itemDescription']
        inventory_itemCount = request.form['itemCount']
        inventory_itemPrice = request.form['itemPrice']
        inventory_itemTotalPrice = float(request.form['itemCount'])*float(request.form['itemPrice'])
        inventory_dateOfProduce = datetime.now().date()
        new_inventory = InventoryItem(itemName=inventory_itemName,itemDescription=inventory_itemDescription,itemCount=inventory_itemCount,itemPrice=inventory_itemPrice,itemTotalPrice=inventory_itemTotalPrice, dateOfProduce=inventory_dateOfProduce)
        db.session.add(new_inventory)
        db.session.commit()
        return redirect('/allitems')
    else:
        itemName = None
        itemDescription = None
        itemCount = None
        itemPrice = None
        form = Forms()
        if form.validate_on_submit():
            itemName = form.itemName.data
            form.itemName.data =''
            itemDescription = form.itemDescription.data
            form.itemDescription.data =''
            itemCount = form.itemCount.data
            form.itemCount.data =''
            itemPrice = form.itemPrice.data
            form.itemPrice.data =''
        return render_template('create.html', itemName = itemName, itemDescription=itemDescription, itemCount = itemCount, itemPrice = itemPrice, form =form)


@app.route('/allitems',methods=['GET'])
def inventory():
    all_inventory=InventoryItem.query.order_by(InventoryItem.dateOfProduce).all()
    return render_template('inventory.html',items=all_inventory )

@app.route('/allitems/delete/<int:id>',methods=['GET','POST'])
def delete(id):
    item = InventoryItem.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(item)
        db.session.commit()
        return redirect('/allitems')
    else:
        return render_template('confirm-delete.html',item=item)

@app.route('/allitems/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    item = InventoryItem.query.get_or_404(id)
    if request.method == 'POST':
        item.itemName = request.form['itemName']
        item.itemDescription = request.form['itemDescription']
        item.itemCount = request.form['itemCount']
        item.itemPrice = request.form['itemPrice']
        item.itemTotalPrice = float(request.form['itemCount'])*float(request.form['itemPrice'])
        item.dateOfProduce = datetime.now().date()
        db.session.commit()
        return redirect('/allitems')
    else:
        form = Forms()
        if form.validate_on_submit():
            itemName = form.itemName.data
            itemDescription = form.itemDescription.data
            itemCount = form.itemCount.data
            itemPrice = form.itemPrice.data
        form.itemName.data = item.itemName
        form.itemDescription.data =item.itemDescription
        form.itemCount.data =item.itemCount
        form.itemPrice.data =item.itemPrice

        return render_template('edit.html',item=item, form=form)

@app.route('/allitems/download',methods=['GET'])
def downloadFile ():
    all_inventory = InventoryItem.query.order_by(InventoryItem.dateOfProduce).all()
    path = "InventoryItemsList.csv"
    with open(path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id',  'itemName', 'itemDescription', 'itemCount', 'itemPrice', 'itemTotalPrice'])
        writer.writeheader()
        for row in all_inventory:
            row_data ={
                "id": row.id,
                "itemName":row.itemName,
                "itemDescription":row.itemDescription,
                "itemCount":row.itemCount,
                "itemPrice":row.itemPrice,
                "itemTotalPrice":row.itemTotalPrice
            }
            writer.writerow(row_data)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)