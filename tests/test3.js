	var a = {},
	b = 'srot',
	stack = {
		'srot': {
				'asd': 123
			}
	},
	_spkElem = function(){},
	spkElemProto = _spkElem[SpkProto] = {
		store: {},
		clone: function(elem){
			stack[b].asd = 155;
			return this.store[elem].cloneNode()
		},
		create: function(elem){
			switch(elem)
			{
			case 'frag':
				console.log(a);
				console.log(a.doc);
				this.store[elem] = a.doc.createDocumentFragment();
				break;
			case 'text':
				this.store[elem] = a.doc.createTextNode('');
				break;
			default:
				this.store[elem] = a.doc.createElement(elem);
			}
		}
	};
