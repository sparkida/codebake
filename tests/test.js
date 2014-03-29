var Dyno = RegExp(/findme/i);
var Dyno2 = RegExp(/=findme/i);
var tep = /=tricky\/=something\/\/\=tofind/i;
/*//if same as last clicked, ignore
if(lastClicked == panelId + part + id)
{
	dbg('panel reload > nothing changed');
	return
}*/
function(c,f)
{
	if((c /= f/2) < 1)
	{
		alert('ekloo')
	}
		return function(panelId, part, id)
		{
			if(!x)
			{
				x = true,
				s = this._save
			}
			//fail invalid
			if(void 0 == panelId || void 0 == part || void 0 == id
				|| ! (typeof panelId == 'string' && panelId.length)
				|| ! (typeof part == 'string' && part.length)
				|| null == id || ! (typeof id == 'string' || typeof id == 'number'))
			{
				throw 'invalid panel reload request'
			}
			//update current with stored obj
			if(void 0 == s[panelId + part + id])
			{
				throw 'invalid panel reload > item not found in store'
			}
			/*//if same as last clicked, ignore
			if(lastClicked == panelId + part + id)
			{
				dbg('panel reload > nothing changed');
				return
			}*/
			//reset lastClicked
			this.lastClicked = panelId + part + id;
			//restore from store ;)
			//empty container
			var pan = this.get(panelId);
			//clearContents	
			Spk.clearChildren(pan[part]);
			//append objV
			pan[part].appendChild(s[this.lastClicked]);	

		}
}
