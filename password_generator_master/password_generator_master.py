import streamlit as st # streamlit is a library for building web apps for machine learning and data science
import random # random is a library for generating random numbers
import string # string is a library for string operations
# define a function to generate a password based on the length and the options selected by the user
def generate_password(Length, use_digits, use_special_chars): # Length is the length of the password, use_digits is a boolean to check if digits are included, use_special_chars is a boolean to check if special characters are included
    characters = string.ascii_letters # ascii_letters is a string of all the letters in the alphabet
    if use_digits: # if use_digits is true
        characters +=string.digits # add the digits to the characters
    if use_special_chars: # if use_special_chars is true
        characters += string.punctuation # add the special characters to the characters
    return ''.join(random.choice(characters) for _ in range(Length)) # return the password
st.title("Password Generator") # title of the app
Length =st.slider("Select the Length of the password", min_value=4, max_value=50, value=16) # slider to select the length of the password
use_digits = st.checkbox("Include digits")  # checkbox to include digits
use_special_chars = st.checkbox("Include special characters") # checkbox to include special characters

if st.button("Generate Password"): # button to generate the password
    password = generate_password(Length, use_digits, use_special_chars)  # generate the password
    # st.success("Generated Password: %s" % password)
    st.success(f"**Generated Password:** `{password}`") # display the password

st.write("---") # write a line to separate the password from the developer's name
st.write("Developed by: [@Sehrish](https://github.com/sehrish-hub)") # write the developer's name and link to their github profile

