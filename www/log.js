// Inspiré de http://krijnhoetmer.nl/irc-logs/

var hlWord = '';
var ol = null;
var statusCheckbox = true;

function createFilterForm() 
{
	ol = document.getElementById('lines');
	if (!ol) return;
	status_chk = document.getElementById('status');
	statusCheckbox = status_chk.checked;
	status_chk.onclick = function() 
	{
		statusCheckbox = this.checked;
		updateFilter();
	};
	hl_txt = document.getElementById('hl_txt');
	hl_btn = document.getElementById('hl_btn');
	hl_txt.onfocus = function() 
	{
		this.select();
	};
	hl_btn.onclick = function() 
	{
		if (hl_txt.value.toLowerCase() != hlWord) 
		{
			hlWord = hl_txt.value.toLowerCase().replace('<', '&lt;').replace('>', '&gt;');
			updateFilter();
		};
	};
};

function updateFilter() 
{
	var lis = ol.getElementsByTagName('li');
	for (var i = 0; i < lis.length; i++) 
	{
		if (lis[i].className != 'filtered') 
		{
			if (statusCheckbox && (lis[i].innerHTML.indexOf(']  ***') != -1)) 
				lis[i].className = 'hide';
			else 
				if (hlWord != '' && 
					lis[i].innerHTML.toLowerCase().indexOf(hlWord) != -1) 
					lis[i].className = 'hl';
				else 
					lis[i].className = '';
		};
	};
};

// Dean Edwards/Matthias Miller/John Resig
function init() 
{
	if (arguments.callee.done) return;
	arguments.callee.done = true;
	if (_timer) clearInterval(_timer);
	if (document.getElementById &&
		document.getElementsByTagName && document.createElement) 
	{
		createFilterForm();
	};
};

if (document.addEventListener) 
{
	document.addEventListener("DOMContentLoaded", init, false);
};
/*@cc_on @*/
/*@if (@_win32)
  document.write("<script id=__ie_onload defer src=javascript:void(0)><\/script>");
  var script = document.getElementById("__ie_onload");
  script.onreadystatechange = function() {
  if (this.readyState == "complete") {
  init();
  };
  };
/*@end @*/

if (/WebKit/i.test(navigator.userAgent)) 
{
	var _timer = setInterval(function() 
	{
		if (/loaded|complete/.test(document.readyState)) 
		{
			init();
		};
	}, 10);
};
window.onload = init;
