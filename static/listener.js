const firstname = document.getElementById('first_name')
const lastname = document.getElementById('last_name')
const streetaddress = document.getElementById('street_address')
const postalcode = document.getElementById('postal_code')
const city_ = document.getElementById('city')
const phonenumber = document.getElementById('phone_number')
const nameoncard = document.getElementById('name_on_card')
const cardnumber = document.getElementById('card_number')
const expirydate = document.getElementById('expiry_date')
const securitycode = document.getElementById('security_code')
//Get all the input fields.

const form = document.getElementById('form');
const error_fields = document.querySelectorAll('.error_message');

//Used to create an array of all inpputs, adding an event listener in the process.
const input_fields = [firstname, lastname, streetaddress, postalcode, city_, phonenumber, nameoncard, cardnumber, expirydate, securitycode];
input_fields.forEach((element, index) => {
  element.addEventListener('input', () => {
    error_fields[index].textContent = '';
    element.classList.remove('input_error');
  });
});
//Waits for the window to finish loading and gets the submit button for validation.
window.onload = function() {
  var submitButton = document.querySelector('button[type="submit"]');
  submitButton.addEventListener('click', function(event) {
    let errors = false;
    let error_message = '';

    //Stops users from checking out with invalid inputs
    for (let loopcount = 0; loopcount < input_fields.length; loopcount++) {
      if (!input_fields[loopcount].value) {
        error_fields[loopcount].textContent = 'This field is required';
        input_fields[loopcount].classList.add('input_error');
        errors = true;
      } else {
        error_fields[loopcount].textContent = '';
        input_fields[loopcount].classList.remove('input_error');
      }
    }
    
    //City validation.
    if (city_.value.match(/\d/)) {
      error_message += 'City must not contain numbers!\n';
      error_fields[4].textContent = 'City must not contain numbers!';
      city_.classList.add('input_error');
      errors = true;
    } else {
      error_fields[4].textContent = '';
      city_.classList.remove('input_error');
    }
  
    //Phone number validation.
    if (isNaN(phonenumber.value) || phonenumber.value.length != 11) {
      error_message += 'Phone number must be 11 digits long and must only contain integers!\n';
      error_fields[5].textContent = 'Phone number must be 11 digits long and must only contain integers!';
      phonenumber.classList.add('input_error');
      errors = true;
    } else {
      error_fields[5].textContent = '';
      phonenumber.classList.remove('input_error');
    }
  
    //Card number validation.
    if (isNaN(cardnumber.value) || cardnumber.value.length != 16) {
      error_message += 'Card number must be 16 digits long and must only contain integers!\n';
      error_fields[7].textContent = 'Card number must be 16 digits long and must only contain integers!';
      cardnumber.classList.add('input_error');
      errors = true;
    } else {
      error_fields[7].textContent = '';
      cardnumber.classList.remove('input_error');
    }
  
    //Expiry date validation.
    if (!expirydate.value.match(/^(0[1-9]|1[0-2])\/\d{2}$/)) {
      error_message += 'Expiry date must be in the format MM/YY! \n';
      error_fields[8].textContent = 'Expiry date must be in the format MM/YY!';
      expirydate.classList.add('input_error');
      errors = true;
    } else {
      error_fields[8].textContent = '';
      expirydate.classList.remove('input_error');
    }
  
    //Security code validation.
    if (isNaN(securitycode.value) || securitycode.value.length !== 3) {
      error_message += 'Security code must be 3 digits!\n';
      error_fields[9].textContent = 'Security code must be 3 digits!';
      securitycode.classList.add('input_error');
      errors = true;
    } else {
      error_fields[9].textContent = '';
      securitycode.classList.remove('input_error');
    }
  
    //Finally display all the potential error messages.
    if (error_message !== '') {
      error_fields.textContent = error_message;
      errors = true;
    }
    
    if (errors) {
      event.preventDefault();
    } else {
      form.submit();
    }
  });
}