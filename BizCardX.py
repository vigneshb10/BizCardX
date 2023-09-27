import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mysql.connector
import base64
from PIL import Image
import re
import os


# connect to sql, create database if not exists and create table with fields
def sql_configuration():
    db = mysql.connector.connect(host="localhost", user="root", password="robertlewandowski")  # establish db connection
    cursor = db.cursor()  # create cursor
    cursor.execute('create database if not exists BizCardX')  # create data BizCardX if not exists
    db.database = 'BizCardX'
    # create table details in database BizCcardX
    cursor.execute('''CREATE TABLE IF NOT EXISTS details  
                   (name TEXT,
                    designation TEXT,
                    company_name TEXT,
                    contact TEXT,
                    alternative VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    street TEXT,
                    city TEXT,
                    state TEXT,
                    pincode VARCHAR(10),
                    image LONGBLOB
                    )''')
    return db, cursor  # return db connection And cursor variable


def page_configuration():  # configuring page layout - Background and Title
    title = 'BizCardX'
    st.markdown(f"<h2 style='color: white; text-align: center;'>{title} </h2>", unsafe_allow_html=True)

    st.markdown(f' <style>.stApp {{\n'
                f'background: url(\'https://cutewallpaper.org/21/light-background-design/Light-Blue-Vector-Triangle'
                f'-Background-Design-Geometric-Background-In-Origami-Style-With-Gradient-Vector-by-Phochi.jpg\');'
                f'\nbackground-size: cover}}\n</style>', unsafe_allow_html=True)


def image_details(image_path):  # extract details from image using easyocr
    extract = easyocr.Reader(['en'])  # initialising reader in en
    result = extract.readtext(image_path)  # use reader to read text from image passed

    details = []  # initialising list variables
    name = []
    designation = []
    contact = []
    email = []
    website = []
    street = []
    city = []
    state = []
    pincode = []
    company = []

    for i in range(len(result)):  # append all the data obtained from result to a list
        details.append(result[i][1])

    for i in range(len(details)):  # for each item in the list extract details
        match1 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+). ([a-zA-Z]+)', details[i])

        match2 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+)', details[i])

        match3 = re.findall('^E.+[a-z]', details[i])

        match4 = re.findall('([A-Za-z]+) ([0-9]+)', details[i])

        match5 = re.findall('([0-9]+ [a-zA-z]+)', details[i])

        match6 = re.findall('([0-9]+)', details[i])

        match7 = re.findall('.com$', details[i])

        if details[i] == details[0]:
            name.append(details[i])
        elif details[i] == details[1]:
            designation.append(details[i])
        elif '-' in details[i]:
            contact.append(details[i])
        elif '@' in details[i]:
            email.append(details[i])
        elif "www " in details[i].lower() or "www." in details[i].lower():

            if details[i][-4:] == '.com':  # if .com is missing
                website.append(details[i])
            else:
                details[i] = details[i].strip('com')
                details[i] = details[i] + '.com'
                website.append(details[i])

        elif "WWW" in details[i]:
            website.append(details[i] + "." + details[i + 1])
        elif match1:
            street.append(match1[0][0])
            city.append(match1[0][1])
            state.append(match1[0][2])
        elif match2:
            street.append(match2[0][0])
            city.append(match2[0][1])
        elif match3:
            city.append(match3[0])
        elif match4:
            state.append(match4[0][0])
            pincode.append(match4[0][1])
        elif match5:
            street.append(match5[0] + ' St,')
        elif match6:
            pincode.append(match6[0])
        elif match7:
            pass
        else:
            company.append(details[i])

    if len(company) > 1:
        comp = company[0] + ' ' + company[1]
    else:
        comp = company[0]

    if len(contact) > 1:  # if contact more than 1 then add it to alternate contact
        contact_number = contact[0]
        alternative_number = contact[1]
    else:
        contact_number = contact[0]
        alternative_number = None

    with open(image_path, 'rb') as image_file:  # open image
        image_data = image_file.read()  # read image
        encoded_image = base64.b64encode(image_data).decode('utf-8')   # convert binary to base64 encoded string

    image_dets = {'name': name[0], 'designation': designation[0], 'company_name': comp,  # create dict of all details
                  'contact': contact_number, 'alternative': alternative_number, 'email': email[0],
                  'website': website[0], 'street': street[0], 'city': city[0], 'state': state[0],
                  'pincode': pincode[0], 'image': encoded_image}

    return image_dets  # return details


def home_configuration():  # home screen configuration
    col1, col2 = st.columns([3, 1])
    col1.header(':blue[Welcome To Business Card Application]')  # display page header
    col1.subheader(':blue[About]')  # display page subheader

    home_text = (f'''In this Streamlit web app, you can upload an image of a business 
                     card and extract relevant information from it using EasyOCR. You can view, 
                     modify, or delete the extracted data in this app. Additionally, the app would 
                     allow users to save the extracted information into a database alongside the 
                     uploaded business card image. The database would be capable of storing multiple entries,
                     each with its own business card image and the extracted information.''')
    col1.markdown(f"<h4 style= text-align: left;'>{home_text} </h4>", unsafe_allow_html=True)  # text display

    col1.subheader(":blue[Technologies Used:]")
    tech_text = 'EasyOCR, Python, SQL, Streamlit'
    col1.markdown(f"<h4  text-align: left;'>{tech_text} </h4>", unsafe_allow_html=True)  # technology display

    ocr_path = os.getcwd() + '\\' + 'ocr_icon.png'
    ocr_image = Image.open(ocr_path)
    col2.image(ocr_image)  # display ocr page icon

    menu = option_menu('', ["Extract & Upload", "Database"],  # create option menus for extract, upload and edit db
                       icons=['cloud-upload', "list-task"],  # icons for options above
                       menu_icon="cast", orientation='horizontal',  # main menu icon and orientation
                       default_index=0,
                       styles={"icon": {"font-size": "20px"},
                               "nav-link": {"font-size": "15px", "text-align": "left", "margin": "-2px",
                                            "--hover-color": "#FFFFFF"},
                               "container": {"max-width": "6000px", "padding": "10px", "border-radius": "5px"},
                               "nav-link-selected": {"background-color": " #2e86c1 "}})  # current selected option color

    if menu == 'Extract & Upload':  # if menu is to extract and upload
        path = ''

        col3, col4 = st.columns([2, 2])

        with col3:
            image_uploaded = st.file_uploader('Choose a file', type=["jpg", "png", "jpeg"])  # user image upload
            extract_button = st.button("Extract & Upload")  # to extract data from image to text

            if image_uploaded is not None:  # if image is uploaded by user
                path = os.getcwd() + "\\" + "card directory" + "\\" + image_uploaded.name  # get path
                image = Image.open(path)  # Open image
                col3.image(image)  # display it for the user

        with col4:
            st.write('')
            st.write('')
            st.info(f'Supported formats - JPEG, JPG & PNG to extract', icon='ℹ️')  # info about file upload and extract
            st.info(f' Click on extract to extract text from image and upload to database', icon='ℹ️')

        if path:
            image_detail = image_details(path)  # call function image details to extract data from image

            if extract_button:
                image_read = cv2.imread(path)  # image read by cv2
                reader = easyocr.Reader(['en'])  # initialise reader from easyocr
                result = reader.readtext(path)  # data extracted

                for data in result:  # loop through data in results
                    top_left = tuple([int(val) for val in data[0][0]])  # set top left coordinates for display purpose
                    bottom_right = tuple([int(val) for val in data[0][2]])  # same as above extracted from result data
                    text = data[1]  # actual data from result
                    font = cv2.FONT_HERSHEY_COMPLEX_SMALL  # set font of highlighted text
                    # highlighting the img extracted from cv2 using coordinates
                    processed_img = cv2.rectangle(image_read, top_left, bottom_right, (0, 255, 0), 2)  # rectangal mark
                    #  mapping text in image
                    processed_img = cv2.putText(processed_img, text, top_left, font, 1, (255, 0, 0), 1, cv2.LINE_AA)
                    plt.figure(figsize=(20, 20))

                col4.subheader("Extracted Text")
                col4.image(image_read)  # display mapped image

                with col3:  # display extracted data from the function
                    st.write('**Name** :', image_detail['name'])
                    st.write('**Designation** :', image_detail['designation'])
                    st.write('**Company Name** :', image_detail['company_name'])
                    st.write('**Contact Number** :', image_detail['contact'])
                    st.write('**Alternative Number** :', image_detail['alternative'])
                    st.write('**E-mail** :', image_detail['email'])

                with col4:
                    st.write('**Website** :', image_detail['website'])
                    st.write('**Street** :', image_detail['street'])
                    st.write('**City** :', image_detail['city'])
                    st.write('**State** :', image_detail['state'])
                    st.write('**Pincode** :', image_detail['pincode'])
                st.divider()

                db, cursor = sql_configuration()  # extract db and cursor variable from function
                try:
                    query = f"SELECT email FROM details WHERE email = '{image_detail['email']}';"  # see if email exists
                    cursor.execute(query)
                    df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
                    df_list = df.values.tolist()
                    email = df_list[0][0]  # result of sql which is email list

                    if image_detail['email'] == email:  # check if email already exists
                        st.warning("Data already exists", icon="⚠")  # display warning if duplicate exists
                    else:
                        pass

                except:  # if email not exists
                    df = pd.DataFrame(image_detail, index=np.arange(1))  # convert extracted data to dataframe
                    df_list = df.values.tolist()  # convert df to list
                    query = "insert into details values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.executemany(query, df_list)  # insert it into the table details
                    db.commit()  # commit database
                    st.success('Data uploaded successfully', icon="✅")

    if menu == 'Database':
        col1, col2 = st.columns([2, 2])
        with col1:
            database_menu = option_menu("", ['Modify', 'Delete'],  # database options are to modify or delete records
                                        menu_icon="list-task",  # icon for menu
                                        default_index=0,
                                        styles={"icon": {"font-size": "20px"},
                                                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px",
                                                             "--hover-color": "#FFFFFF"},
                                                "nav-link-selected": {"background-color": " #2e86c1 "}})  # highlist sel

        db, cursor = sql_configuration()

        if database_menu == 'Modify':  # if option selected is modify
            card_holder = {}  # create dict
            cursor.execute("SELECT name FROM bizcardx.details")  # list of names of cardholder to choose from
            result = cursor.fetchall()  # fetch results

            for name in result:  # extract data from results
                card_holder[name[0]] = name[0]  # create dictionary and use the dict.keys

            # select box with list of cardholders to edit data
            selected_cardholder = st.selectbox("Select a card holder name to update", card_holder.keys(), key='modify')
            cursor.execute("SELECT * FROM bizcardx.details WHERE name=%s", (selected_cardholder,))  # selected user data
            result = cursor.fetchone()

            if result is not None:
                name = st.text_input("Name", result[0])  # display each fields as text_input to edit
                designation = st.text_input("Designation", result[1])
                company_name = st.text_input("Company Name", result[2])
                contact = st.text_input("Contact", result[3])
                alternative = st.text_input("Alternative", result[4])
                email = st.text_input("Email", result[5])
                website = st.text_input("Website", result[6])
                street = st.text_input("Street", result[7])
                city = st.text_input('City', result[8])
                state = st.text_input("State", result[9])
                pincode = st.text_input("Pincode", result[10])

                if st.button("Modify"):
                    # Update the information for the selected business card in the database
                    cursor.execute(   # update edited details to database
                        'UPDATE bizcardx.details SET name=%s, designation=%s, company_name=%s, contact=%s, '
                        'alternative=%s, email=%s, website=%s, street=%s, city=%s, state=%s, pincode=%s WHERE name=%s',
                        (name, designation, company_name, contact, alternative, email, website, street, city, state,
                         pincode, selected_cardholder))
                    db.commit()  # commit database

                    cursor.execute(
                        f"SELECT name, designation, company_name, contact, alternative, email, website,  street, "
                        f"city, state, pincode FROM bizcardx.details WHERE name= '{selected_cardholder}'")
                    result = cursor.fetchall()  # fetch updated details
                    df = pd.DataFrame(result, columns=['Name', 'Designation', 'Company_Name', 'Contact', 'Alternative',
                                                       'Email', 'Website', 'Street', 'City', 'State', 'Pincode'])
                    st.table(df)  # show updated details
                    st.success("Data modified successfully")

        db, cursor = sql_configuration()

        if database_menu == 'Delete':  # to delete records
            card_holder = {}
            cursor.execute("SELECT name FROM bizcardx.details")  # fetch list of card holders
            result = cursor.fetchall()

            for name in result:
                card_holder[name[0]] = name[0]

            # create select box using dict.keys()
            selected_cardholder = st.selectbox("Select a card holder name to delete", card_holder.keys(), )

            if st.button('Delete'):  # if delete
                query = f"delete from details where name = '{selected_cardholder}'"  # execute delete for selected key
                cursor.execute(query)
                db.commit()  # db commit
                st.experimental_rerun()
                st.success("Data Deleted successfully", icon='✅')


icon = Image.open('pageicon.png')
st.set_page_config(page_title="BizCardX", page_icon=icon, layout="wide")
sql_configuration()
page_configuration()
home_configuration()
