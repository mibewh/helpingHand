function popup(url) {
	newwindow=window.open(url,'name','height=500,width=800');
	if (window.focus) {newwindow.focus()}
	return false;
}