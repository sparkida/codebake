(function(w)
{
	asd = ['asdasd','asdasdads','asfdasf','asfasf'];

	a[getJSON] = (function()
	{
		var getTimer = function(url)
		{
			var timer, geturl = url,
			getContent = function()
			{
				var scripts = Spk.get('script');
				for(i = 0; i < scripts.length; i++)
				{
					if(scripts[i].hasAttribute('src') && scripts[i].src === geturl)
					{
						capture = scripts[i]
						Spk.win.clearInterval(timer)
						timer = null
						break
					}
				}
			};

			timer = Spk.win.setInterval(getContent, 1);	
		};

		return function(url, async)
		{
			var geturl = url;
			a.getScript(geturl);
			new getTimer(geturl);
		}		
	}()),

	a.docHeight = function()
	{
		return a.doc.documentElement.offsetHeight
	},

	a.docWidth = function()
	{
		return a.doc.documentElement.offsetWidth
	},

	/* 
	 * ClientHeight and ClientWidth
	 * returns a crossbrowser way to retrieve each
	 */
	(function()
	{
		var compat = a.doc.compatMode.toLowerCase() === 'backcompat' ? true : false;

		a[clientHeight] = function()
		{
			return compat 
			? a.body[clientHeight]
			: a.doc.documentElement[clientHeight]
		},
		a[clientWidth] = function()
		{
			return compat 
			? a.body[clientWidth]
			: a.doc.documentElement[clientWidth]
		}
	}());
	a[getScript] = function(src, async)
	{
		//determine queryString
		var src,
		bool = Spk.win['Boolean'],
		proto = src.split('://'),
		//split by slash and remove empty parts(ie<9)
		parts = a.filter(proto.pop().split('/'), bool),
		basename = parts.pop(),
		version = basename.search(/\?v=/) >= 0 ? basename.split('?') : '';
		
		//set the version and trim the added .js extension if any
		if(version.length > 0)
		{
			basename = version[0];
			version = version.pop();

			//return substr if version has an added extension
			if(version.search(/\.js/) >= 0)
			{
				version = version.substr(0, version.length - 3)
			}
			//set new src
			src = proto + '://' + parts.join('/') + '/' + basename + '?' + version			
		}
	}
	core_pnum = /[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source,
			( ~b.sourceIndex || MAX_NEGATIVE ) -
			( ~a.sourceIndex || MAX_NEGATIVE );
	// Use IE sourceIndex if available on both nodes
		jQuery.each( jQuery.expr.match.bool.source.match( /\w+/g ), function( i, name ) {
		// Keys separate source (or catchall "*") and destination types with a single space
	}

}(window))
