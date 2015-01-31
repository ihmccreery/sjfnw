'use strict';
// constants
var STATUS_TEXTS = { // for ajax error messages
  400: '400 Bad request',
  401: '401 Unauthorized',
  403: '403 Forbidden',
  404: '404 Not found',
  408: '408 Request timeout',
  500: '500 Internal server error',
  503: '503 Service unavailable',
  504: '504 Gateway timeout'
};

// general display
function datepicker() { // date input fields
  $.datepicker.setDefaults({
    dateFormat: 'mm/dd/yy',
    minDate: 0,
    hideIfNoPrevNext: true,
    constrainInput: false
  });
  $('.datePicker').datepicker();
}

// ajax - general
var requestProcessing = false;
function startProcessing() {
  requestProcessing = true;
  // console.log('Request processing');
  var loader = document.getElementById('ajax_loading');
  if (loader) {
    loader.style.display = '';
  }
}

function endProcessing() {
  requestProcessing = false;
  // console.log('Request complete');
  var loader = document.getElementById('ajax_loading');
  if (loader) {
    loader.style.display = 'none';
  }
}

/* Submits form data, displays errors or redirects if successful */
function Submit(subUrl, formId, divId, date, dasked, dpromised){
  if (requestProcessing) {
    console.log('Request processing; submit denied');
    return false;
  }
  startProcessing();
  console.log('Submission to ' + subUrl + ' requested');
  $.ajax({
    url: subUrl,
    type: 'POST',
    data: $(formId).serialize(),
    timeout: 10000,
    success: function(data, textStatus, jqXHR){
      trackEvents(subUrl, divId, 'POST');
      if (jqXHR.responseText === 'success') { // successful
        console.log('Submission to ' + subUrl + ' returned success; redirecting');
        if (subUrl.match('add-contacts')) {
          setTimeout(function() {
            location.href = '/fund/?load=stepmult#your-contacts';
          }, 200);
        } else {
          setTimeout(function() {
            location.href = '/fund/';
          }, 200);
        }
      } else { // errors
        console.log('Submission to ' + subUrl + ' returned text');
        document.getElementById(divId).innerHTML = jqXHR.responseText;
        if (subUrl.match('done')) {
          var pks = subUrl.match(/\d+/g);
          if (pks && pks[1]) {
            completeLoaded(pks[1], dasked, dpromised, 'True');
          }
        }
      }
      if (date) { datepicker();}
      endProcessing();
    },
    error: function(jqXHR, textStatus){
      endProcessing();
      var errortext = '';
        if (STATUS_TEXTS[jqXHR.status]) {
          errortext = STATUS_TEXTS[jqXHR.status];
        } else if (textStatus === 'timeout') {
          errortext = 'Request timeout';
        } else {
          errortext = (jqXHR.status || '') + ' Unknown error';
        }
      document.getElementById(divId).innerHTML = '<p>An error occurred while handling your request.  We apologize for the inconvenience.</p><p>URL: POST ' + subUrl + '<br>Error: ' + errortext + '</p><p><a href="/fund/support" target="_blank">Contact us</a> for assistance if necessary.  Please include the above error text.</p>';
        console.log('Error submitting to ' + subUrl + ': ' + errortext);
      if (date) {
        datepicker();
      }
    }
  });
}

// analytics events
function trackEvents(url, divId, reqType) { // analytics events
  // console.log('trackEvents', url, divId, reqType);
  var category;
  var action;
  if (divId.search('addmult') > -1) {
    // console.log('addmult');
    if (reqType === 'POST') {
      action = 'Add multiple - submit';
    } else {
      action = 'Add multiple - load';
    }
    if (url.search('addmult') > -1) {
      category = 'Contacts';
    } else if (url.search('stepmult') > -1) {
      category = 'Steps';
    }
  } else if (divId.search('nextstep') > -1) {
    // console.log('nextstep');
    category = 'Steps';
    if (url.search(/\d+$/) > -1 && reqType === 'POST') {
      action = 'Edit';
    } else if (url.search(/done$/) > -1) {
      if (reqType === 'POST') {
        action = 'Complete step - submit';
      } else {
        action = 'Complete step - load';
      }
    }
  } else if (reqType === 'POST') {
    // console.log('POST');
    if (url.search(/step$/) > -1) {
      category = 'Steps';
      action = 'Add';
    } else if (url.search(/delete$/) > -1) {
      category = 'Contacts';
      action = 'Delete';
    } else if (url.search(/edit$/) > -1) {
      category = 'Contacts';
      action = 'Edit';
    }
  }
  console.log('trackEvents', category, action);
    if (category && action) {
      _gaq.push(['_trackEvent', category, action]);
    }
}

// suggested steps
var suggestionsDiv;
function showSuggestions(inp) { // shows suggested steps
  if (suggestionsDiv) { suggestionsDiv.style.display = 'none'; } // hides prior set
  var patt = new RegExp('\\d+');
  var num = patt.exec(inp);
  suggestionsDiv = document.getElementById('suggest_' + num);
  suggestionsDiv.style.display = 'block';
}

function suggestFill(source, target) { // fills input with selected step
  var text = source.innerHTML;
  if (target) {
    document.getElementById(target).value = text;
  } else {
    document.getElementById('id_description').value = text;
  }
}
