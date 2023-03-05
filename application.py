from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

application = Flask(__name__)
app = application

@app.route('/', methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            input_str = request.form['content'].replace(" ","")
            flip_url = "https://www.flipkart.com/search?q=" + input_str
            uClient = uReq(flip_url)
            flip_page = uClient.read()
            uClient.close()
            flipkart_html = bs(flip_page, "html.parser")
            comment_div = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del comment_div[0:3]
            box = comment_div[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            productRequest = requests.get(productLink)
            productRequest.encoding='utf-8'
            ProductHtml = bs(productRequest.text, "html.parser")
            print(ProductHtml)
            commentboxes = ProductHtml.find_all('div', {'class': "_16PBlm"})

            filename = input_str + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for i_comment in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = i_comment.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = i_comment.div.div.div.div.text
                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = i_comment.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'

                try:
                    comment_tag = i_comment.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    comment = comment_tag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": input_str, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": comment}
                reviews.append(mydict)

            
            client = pymongo.MongoClient("mongodb+srv://AJAmit17:amit6969@cluster0.gmvsjwi.mongodb.net/?retryWrites=true&w=majority")
            db = client['Scrap_']
            scrap_data = db['Result_data_']
            scrap_data.insert_many(reviews)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
    #app.run(debug=True)
