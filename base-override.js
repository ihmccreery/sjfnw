/* Highlight */
$( document ).ready(function() {
    hljs.initHighlightingOnLoad();
    $('table').addClass('table');
});

$('body').scrollspy({
    target: '.bs-sidebar',
});

/* Prevent disabled links from causing a page reload */
$("li.disabled a").click(function() {
    event.preventDefault();
});
