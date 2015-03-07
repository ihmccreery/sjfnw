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

/* Used in MassStep form to show suggested for currently focused step */
var suggestionsDiv;
function showSuggestions(inp) { // eslint-disable-line no-unused-vars
  if (suggestionsDiv) { suggestionsDiv.style.display = 'none'; } // hides prior set
  var patt = new RegExp('\\d+');
  var num = patt.exec(inp);
  suggestionsDiv = document.getElementById('suggest_' + num);
  suggestionsDiv.style.display = 'block';
}

/* Fills in the description field when a suggestion is clicked */
function suggestFill(source, target) { // eslint-disable-line no-unused-vars
  var text = source.innerHTML;
  if (target) {
    document.getElementById(target).value = text;
  } else {
    document.getElementById('id_description').value = text;
  }
}

/* Show/hide donor details */
function toggle(a, b) { // eslint-disable-line no-unused-vars
  // toggles a, border on b if a is shown
  var e = $('#' + a);
  var f = $('#' + b);
  if (e.length === 0) {
    return;
  }
  e.toggle();
  f.toggleClass('donor-border');
}

/* step complete form - promise input changed */
function promised(donorId, show) {
  // show or hide the last name & contact info fields
  var followupClass = '#' + donorId + '_promise_follow';
  var promiseAmount = '#' + donorId + '_promise';
  if (show) {
    $(promiseAmount).show();
    $(followupClass).show('drop');
  } else {
    $(promiseAmount).hide();
    $(followupClass).hide();
  }
}

function responseSelected(response) {
  // show or hide the promised field
  // called when step complete form - response input changed
  var donorId = response.id.match(/\d+/);
  // var promisedSpan = document.getElementById(donorId + '_promise');
  console.log(typeof response.value);
  if (response.value === '1') { // 1 = promised, 2 = unsure, 3 = dec
    console.log('in respselected, calling promise entered');
    promised(donorId, true);
  } else {
    console.log('in respselected, calling promise entered hide');
    promised(donorId, false);
  }
}

function askedToggled(asked) {
  // show or hide the response field
  // called by step complete form - asked input changed
  var num = asked.id.match(/\d+/);
  var responseSpan = document.getElementById(num + '_response');
  if (asked.checked) {
    // console.log('askedtoggled checked');
    responseSpan.style.display = 'inline';
    var response = document.getElementById(num + '_id_response');
    responseSelected(response);
  } else { // hide all following
    // console.log('askedtoggled un checked');
    responseSpan.style.display = 'none';
    var hideSpan = document.getElementById(num + '_promise');
    hideSpan.style.display = 'none';
    promised(num, false);
  }
}

// complete step form
function completeLoaded(pk, dasked, dpromised, submitted) {
  // hide fields based on what is already in the database for the contact
  // console.log('completeloaded called, submitted is ' +submitted);
  var askedSpan = $('#' + pk + '_asked');
  var responseSpan = $('#' + pk + '_response');
  var promisedSpan = $('#' + pk + '_promise');
  if (dasked !== 'False') {  // have asked
    askedSpan.hide();
    if (dpromised !== 'None') { // promise complete, hide 2&3
      responseSpan.hide();
      promisedSpan.hide();
    } else { // check response field
      var response = $('#' + pk + '_id_response');
      responseSelected(response);
    }
  } else { // haven't asked yet, hide 2&3
    responseSpan.hide();
    promisedSpan.hide();
    if (submitted) {
      var asked = document.getElementById(pk + '_id_asked');
      askedToggled(asked);
    }
  }
  // follow up is hidden by defalt, don't need to hide it
}

function loadView(getUrl, divId, dasked, dpromised) {
  if (requestProcessing) {
    console.log('Request processing; load view denied');
    return false;
  }
  console.log(getUrl + ' load requested');
  startProcessing();
  $.ajax({
    url: getUrl,
    type: 'GET',
    timeout: 10000,
    success: function(data, textStatus, jqXHR) {
      console.log(getUrl + ' loaded');
      document.getElementById(divId).innerHTML = jqXHR.responseText; // fill the div
      var pks = getUrl.match(/\d+/g);
      if (pks && pks[1]) { // donor-specific form loading
        var a = document.getElementById('donor-' + pks[0]);
        a.style.borderColor = '#555';
        if (dasked) {
          completeLoaded(pks[1], dasked, dpromised);
        }
      } else if (divId === 'addmult') {
        document.getElementById(divId).style.borderColor = '#555';
      }
      datepicker();
      trackEvents(getUrl, divId, 'GET');
      endProcessing();
    },
    error: function(jqXHR, textStatus) {
      endProcessing();
      var errortext = '';
      if (STATUS_TEXTS[jqXHR.status]) {
        errortext = STATUS_TEXTS[jqXHR.status];
      } else if (textStatus === 'timeout') {
        errortext = 'Request timeout';
      } else {
        errortext = (jqXHR.status || '') + ' Unknown error';
      }
      console.log('Error loading ' + getUrl + ': ' + errortext);
      document.getElementById(divId).innerHTML = '<p>An error occurred while handling your request.  We apologize for the inconvenience.</p><p>URL: ' + getUrl + '<br>Error: ' + errortext + '</p><p><a href="/fund/support" target="_blank">Contact us</a> for assistance if necessary.  Please include the above error text.</p>';
    }
  });
}

/* Submits form data, displays errors or redirects if successful */
function Submit(subUrl, formId, divId, date, dasked, dpromised) { // eslint-disable-line no-unused-vars
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
    success: function(data, textStatus, jqXHR) {
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
      if (date) { datepicker(); }
      endProcessing();
    },
    error: function(jqXHR, textStatus) {
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

$(document).ready(function() {
  $('.load').each(function(i, el) {
    var $el = $(el);
    var url = $el.data('url');
    var target = $el.data('target');
    if (url && target) {
      $el.on('click', function() {
        loadView(url, target);
      });
    }
  });
});
