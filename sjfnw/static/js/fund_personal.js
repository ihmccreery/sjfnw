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

// date input fields
function datepicker() {
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
function startProcessing(containerId) {
  requestProcessing = true;
  var loader = $('#' + containerId).find('.ajax-loading');
  if (loader) {
    loader.show();
  }
}

function endProcessing() {
  requestProcessing = false;
  $('.ajax-loading').hide();
}

// analytics events
function trackEvents(url, divId, reqType) {
  var category;
  var action;
  if (divId.search('addmult') > -1) {
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

/* Display suggested steps for currently focused input field
 * @param {string} inputId - id of currently focused step description input field
 * Used in MassStep form to show only one set of suggested steps at a time */
var suggestionsDiv;
function showSuggestions(inputId) { // eslint-disable-line no-unused-vars
  if (suggestionsDiv) {
    // hide prior set
    suggestionsDiv.style.display = 'none';
  }
  var patt = new RegExp('\\d+');
  var num = patt.exec(inputId);
  suggestionsDiv = document.getElementById('suggest_' + num);
  suggestionsDiv.style.display = 'block';
}

/* Fills in the description field when a suggestion is clicked
 * @param {Element} source - selected suggested step
 * @param {string} target - id of the field to fill in
 */
function suggestFill(source, target) { // eslint-disable-line no-unused-vars
  var text = source.innerHTML;
  if (target) {
    document.getElementById(target).value = text;
  } else {
    document.getElementById('id_description').value = text;
  }
}

/* Show/hide donor details. Border around donor when shown. */
function toggle(detailsId, donorId) { // eslint-disable-line no-unused-vars
  var details = $('#' + detailsId);
  var donor = $('#' + donorId);
  if (details.length === 0) {
    return;
  }
  details.toggle();
  donor.toggleClass('donor-border');
}

/* Show or hide promise & followup fields if 'promise' response is selected
 * @param {string} donorId - donor.pk as string
 * @param {boolean} show - true to show, otherwise hide
 */
function promised(donorId, show) {
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

/* Show or hide the promise field based on response value
 * @param {Element} response - responce select element
 * Called by onchange of response field or on load/submit of form
 */
function responseSelected(response) {
  var donorId = response.id.match(/\d+/);
  if (response.value === '1') { // 1 = promised, 2 = unsure, 3 = dec
    promised(donorId, true);
  } else {
    promised(donorId, false);
  }
}

/* Show or hide response & promise fields based on whether asked is checked
 * @param {Element} asked - the asked checkbox
 * Called by onclick of asked checkbox, or when form is loaded/reloaded
 */
function askedToggled(asked) {
  var num = asked.id.match(/\d+/);
  console.log(asked);
  var responseSpan = document.getElementById(num + '_response');
  if (asked.checked) {
    responseSpan.style.display = 'inline';
    var response = document.getElementById(num + '_id_response');
    responseSelected(response);
  } else { // hide all following
    responseSpan.style.display = 'none';
    var hideSpan = document.getElementById(num + '_promise');
    hideSpan.style.display = 'none';
    promised(num, false);
  }
}

/* Initiate show/hide of appropriate sections after compete step form is loaded
 * @param {number} pk - donor.pk
 * @param {boolean} dasked - donor.asked (from the saved model, not form)
 * @param {boolean} dpromised - donor.promised (from the saved model, not form)
 * @param {string} [submitted] - 'True' if this is a form reload after POST, else undefined
 */
function completeLoaded(pk, dasked, dpromised, submitted) {
  var askedSpan = $('#' + pk + '_asked');
  var responseSpan = $('#' + pk + '_response');
  var promisedSpan = $('#' + pk + '_promise');
  if (dasked !== 'False') {  // have asked
    askedSpan.hide();
    if (dpromised !== 'None') { // promise complete, hide 2&3
      responseSpan.hide();
      promisedSpan.hide();
    } else { // check response field
      var response = document.getElementById(pk + '_id_response');
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
}

/* Load a form into the page via ajax request
 * @param {string} getUrl - url to fetch
 * @param {string} divId - id of the element to load the received content into
 * @param {boolean} [dasked] - donor.asked (from saved model)
 * @param {boolean} [dpromised] - donor.promised (from saved model)
 * dasked and dpromised are only provided when loading a complete step form.
 */
function loadView(getUrl, divId, dasked, dpromised) {
  if (requestProcessing) {
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

/* Submit form data via ajax request.
 * Redirects on success, otherwise displays form with errors
 * @param {string} subUrl - url to send the POST request to
 * @param {string} formId - id of the form element
 * @param {string} divId - id of the element to load the form with errors into
 * @param {boolean} [date] - true if form contains date elements
 * @param {boolean} [dasked] - donor.asked (from saved model)
 * @param {boolean} [dpromised] - donor.promised (from saved model)
 */
function Submit(subUrl, formId, divId, date, dasked, dpromised) { // eslint-disable-line no-unused-vars
  if (requestProcessing) {
    console.log('Request processing; submit denied');
    return false;
  }
  startProcessing(divId);
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
        console.log('Submission to ' + subUrl + ' returned text (errors)');
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

/**
 * Add a row to the add contacts form
 *
 * Clones the last row, increments its form id, updates the formset management form
 */
function addRow() { // eslint-disable-line no-unused-vars
  var formCount = $('#id_form-TOTAL_FORMS').val();

  var lastRow = $('.form-row:last');
  var newElement = lastRow.clone(true);

  // reset field values, increment form number
  newElement.find(':input').each(function() {
    var input = $(this);
    input.val('').removeAttr('checked');
    var name = input.attr('name').replace(/-\d+-/, '-' + formCount + '-');
    input.attr({'name': name, 'id': 'id_' + name});
  });

  // update labels to point to correct inputs
  newElement.find('label').each(function() {
    var label = $(this);
    var newFor = label.attr('for').replace(/-\d+-/, '-' + formCount + '-');
    label.attr('for', newFor);
  });

  // remove any cloned errors
  newElement.find('.errorlist').remove();

  $('#id_form-TOTAL_FORMS').val(++formCount);
  lastRow.after(newElement);
}

/* Set up click handlers for loadView */
$(document).ready(function() {
  $('.load').each(function(i, el) {
    var $el = $(el);
    var url = $el.data('url');
    var target = $el.data('target');
    var asked = $el.data('asked');
    var pro = $el.data('promised');
    if (url && target) {
      $el.on('click', function() {
        loadView(url, target, asked, pro);
      });
    }
  });
});
