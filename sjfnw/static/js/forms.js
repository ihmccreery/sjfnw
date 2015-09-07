'use strict';
/** Shared form functions - utils, autosave, file handling **/

/**----------------------------- formUtils ---------------------------------**/
var formUtils = {};

formUtils.loadingImage = '<img src="/static/images/ajaxloader2.gif" height="16" width="16" alt="Loading...">';

formUtils.statusTexts = { // for ajax error messages
  400: '400 Bad request',
  401: '401 Unauthorized',
  403: '403 Forbidden',
  404: '404 Not found',
  408: '408 Request timeout',
  500: '500 Internal server error',
  503: '503 Service unavailable',
  504: '504 Gateway timeout'
};


/**
 * @param {string} urlPrefix - beginning of path (i.e. 'apply'). no slashes
 * @param {number} draftId - pk of draft object (draft app or draft yer)
 * @param {number} submitId - pk of object used in post (cycle or award)
 * @param {string.alphanum} userId - randomly generated user id for mult edit warning
 * @param {string} staffUser - querystring for user override (empty string if n/a)
 */
formUtils.init = function(urlPrefix, draftId, submitId, userId, staffUser) {
  if (staffUser && staffUser !== 'None') {
    formUtils.staffUser = staffUser;
  } else {
    formUtils.staffUser = '';
  }
  autoSave.init(urlPrefix, submitId, userId);
  fileUploads.init(urlPrefix, draftId);
};


/**
 * Return current time as a string for display. Format: May 12, 2:45p.m.
 */
formUtils.currentTimeDisplay = function() {
  var monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'];
  var d = new Date();
  var h = d.getHours();
  var m = d.getMinutes();
  var dd = 'a.m.';
  if (h >= 12) {
    h = h - 12;
    dd = 'p.m.';
  }
  h = h === 0 ? 12 : h;
  m = m < 10 ? '0' + m : m;
  return monthNames[d.getMonth()] + ' ' + d.getDate() + ', ' + h + ':' + m + dd;
};


/**
 * Return current time as a string for console logs. Format: hh:mm:ss
 */
formUtils.logTime = function () {
  var d = new Date();
  var m = d.getMinutes();
  m = m < 10 ? '0' + m : m;
  return d.getHours() + ':' + m + ':' + d.getSeconds() + ' ';
};


/**
 * Update word limit indicator for text field. TODO rename
 *
 * @param {HTMLElement} area - textarea element
 * @param {number} limit - word limit for that field
 */
function charLimitDisplay(area, limit) {
  var counter = document.getElementById(area.name + '_counter');
  var words = area.value.match(/[^ \r\n]+/g) || [];
  var diff = limit - words.length;
  if (diff >= 0) {
    counter.innerHTML = diff + ' words remaining';
    counter.className = 'char_counter_ok';
  } else {
    counter.innerHTML = -diff + ' words over the limit';
    counter.className = 'char_counter_over';
  }
}

/**------------------------------- autoSave --------------------------------**/

var autoSave = {};
autoSave.saveTimer = false;
autoSave.pauseTimer = false;

/* autosave flow:

   page load -> --> init ->
   page blur -> pause() -> sets onfocus, sets pauseTimer -30-> clears saveTimer

*/

autoSave.init = function(urlPrefix, submitId, userId) {
  autoSave.submitUrl = '/' + urlPrefix + '/' + submitId;
  autoSave.saveUrl = autoSave.submitUrl + '/autosave' + formUtils.staffUser;
  autoSave.submitUrl += formUtils.staffUser;
  if (userId) {
    autoSave.userId = userId;
  } else {
    autoSave.userId = '';
  }
  console.log('Autosave variables loaded');
  autoSave.resume();
};


autoSave.pause = function() {
  if ( !window.onfocus ) {
    console.log(formUtils.logTime() + 'autoSave.pause called; setting timer');
    // pause auto save
    autoSave.pauseTimer = window.setTimeout(function() {
       console.log(formUtils.logTime() + 'autoSave.pauseTimer up, pausing autosave');
       window.clearInterval(autoSave.saveTimer);
       autoSave.pauseTimer = false;
       }, 30000);
    // set to resume when window gains focus
    $(window).on('focus', autoSave.resume);
    // don't watch for further blurs
    $(window).off('blur');
  } else {
    console.log(formUtils.logTime() + 'autoSave.pause called, but already paused');
  }
};

autoSave.resume = function() {
  if ( !window.onblur ) { // avoid double-firing
    console.log(formUtils.logTime() + ' autoSave.resume called');
    // reload the pause binding
    $(window).on('blur', autoSave.pause);
    if (autoSave.pauseTimer) {
      // clear timer if window recently lost focus (autosave is still going)
      console.log('pause had been set; clearing it');
      window.clearTimeout(autoSave.pauseTimer);
      autoSave.pauseTimer = false;
    } else {
      // set up save timer
      console.log('Setting autosave interval');
      autoSave.saveTimer = window.setInterval('autoSave.save()', 30000); // TODO should this be without parens?
    }
    // unload the resume binding
    $(window).off('focus');
  } else {
    console.log(formUtils.logTime() + ' window already has onblur');
  }
};

autoSave.save = function (submit, force) {
  if (!force) { force = 'false'; }
  if (formUtils.staffUser) { // TODO use querystring function
    force = '&force=' + force;
  } else {
    force = '?force=' + force;
  }
  console.log(formUtils.logTime() + 'autosaving');
  $.ajax({
    url: autoSave.saveUrl + force,
    type: 'POST',
    data: $('form').serialize() + '&user_id=' + autoSave.userId,
    success: function(data, textStatus, jqXHR) {
      if (jqXHR.status === 200) {
        if (submit) { // trigger the submit button
          var submitAll = document.getElementById('hidden_submit_app');
          submitAll.click();
        } else { // update 'last saved'
          $('.autosaved').html(formUtils.currentTimeDisplay());
        }
      } else { // unexpected status code
        $('.autosaved').html('Unknown error<br>If you are seeing errors repeatedly please <a href="/apply/support#contact">contact us</a>');
      }
    },
    error: function(jqXHR, textStatus) {
      var errortext = '';
      if (jqXHR.status === 409)  { // conflict - pause autosave and confirm force
        window.clearInterval(autoSave.saveTimer);
        showConflictWarning(2); // defined in org_app.html
      } else {
        if(jqXHR.status === 401) {
          location.href = jqXHR.responseText + '?next=' + location.href;
        } else if (formUtils.statusTexts[jqXHR.status]) {
          errortext = formUtils.statusTexts[jqXHR.status];
        } else if (textStatus === 'timeout') {
          errortext = 'Request timeout';
        } else {
          errortext = 'Unknown error';
        }
        $('.autosaved').html('Error: ' + errortext + '<br>If you are seeing errors repeatedly please <a href="/apply/support#contact">contact us</a>');
      }
    }
  });
};

/**------------------------------------ FILE UPLOADS -------------------------------------------**/
var fileUploads = {};

fileUploads.uploading = false;
fileUploads.uploadingSpan = '';
fileUploads.currentField = '';

fileUploads.init = function(urlPrefix, draftId) {
  fileUploads.getUrl = '/get-upload-url/?type=' + urlPrefix + '&id=' + draftId;
  fileUploads.removeUrl = '/' + urlPrefix + '/' + draftId + '/remove/';
  $("[type='file']").change(function() {
      fileUploads.fileChanged(this.id);
    });
  console.log('fileUploads vars loaded, file fields scripted');
  $('.default-file-input').children('a').remove();
};

/* each file field has its own form. html element ids use this pattern:
  input field: 							'id_' + fieldname
  form: 										fieldname + '_form'
  span for upload status: 	fieldname + '_uploaded'
  submit button: 						fieldname + '_submit' */

fileUploads.clickFileInput = function(event, inputId) {
  /* triggered when 'choose file' label is clicked
     transfers the click to the hidden file input */
  console.log(event);
  console.log('clickFileInput' + inputId);
  var input = document.getElementById(inputId);
  if (input) {
    input.control.click();
    console.log('Clicked it');
  } else {
    console.log('Error - no input found');
  }
};

fileUploads.fileChanged = function(fieldId) {
  /* triggered when a file is selected
     show loader, call getuploadurl */
  console.log('fileChanged');
  if (fileUploads.uploading) {
    console.log('Upload in progress; returning');
    return false;
  }
  console.log(fieldId + ' onchange');
  var file = document.getElementById(fieldId).value;
  console.log('Value: ' + file);
  if (file) {
    fileUploads.uploading = true;
    fileUploads.currentField = fieldId.replace('id_', '');
    fileUploads.uploadingSpan = document.getElementById(fieldId.replace('id_', '') + '_uploaded');
    fileUploads.uploadingSpan.innerHTML = formUtils.loadingImage;
    fileUploads.getUploadURL();
  }
};

fileUploads.getUploadURL = function() {
  console.log('getUploadURL');
  $.ajax({
    url: fileUploads.getUrl,
    success: function(data) {
      console.log('current field: ' + fileUploads.currentField);
      var cform = document.getElementById(fileUploads.currentField + '_form');
      cform.action = data;
      var cbutton = document.getElementById(fileUploads.currentField + '_submit');
      cbutton.click();
    }
  });
};

fileUploads.iframeUpdated = function(iframe) { // process response
  console.log(formUtils.logTime() + 'iframeUpdated');
  var results = iframe.contentDocument.body.innerHTML;
  console.log('The iframe changed! New contents: ' + results);
  if (results) {
    var fieldName = results.split('~~')[0];
    var linky = results.split('~~')[1];
    var fileInput = document.getElementById('id_' + fieldName);
    if (fileInput && linky) {
      fileUploads.uploadingSpan.innerHTML = linky;
    } else {
      fileUploads.uploadingSpan.innerHTML = 'There was an error uploading your file. Try again or <a href="/apply/support">contact us</a>.';
    }
    fileUploads.uploading = false;
  }
};

fileUploads.removeFile = function(fieldName) {
  $.ajax({
    url: fileUploads.removeUrl + fieldName + formUtils.staffUser,
    success: function() {
      var rSpan = document.getElementById(fieldName + '_uploaded');
      rSpan.innerHTML = '<i>no file uploaded</i>';
    }
  });
};
