var ENV;
var mainLayout;
var w = window.innerWidth,
    h = window.innerHeight;
var link,node;
var minLinkDistance=0,scale=1;
var margins = 10;
var ticker,counter;
var friends,me;
var strings = ["We Are Working.","Please wait while we fetch your closest friends","Working","Working.","Working..","Working...","Still Working",
                        "We are really sorry!!","Its your first time","So we are building your profile from scratch","Please bear with us","This won't happen next time",
                        "Almost done","really almost done","just a few more moments","We will make sure, you don't regret the wait","Yep! It's that good",
                        "About to be done","Do let us know, how it is","We are building something really from scratch","Your likes","Your posts","Your messages",
                        "Your Tags","These things tell us who is close to you","It's all you","You'll see",":)",":D",":p",";)",";p","That was something","!!!",
                        "We will be there","Don't worry","You can brew yourself a cup of coffee","We will keep track of thing while this is still working",
                        ":D"];


var dummyServer = new Object();

dummyServer.restCall = function(restString,callback){
    var reststr = restString.split("?");
    var ret = me;
    ret["friends"]=friends;
    callback((reststr[0] == "me") ? ret : friends);
}

function weAreWorkingAnimation(){
	counter =0 ;
	var anim = d3.select("body").append("div").attr("id","overlay").append("svg").attr("width",w).attr("height",h);
	console.log("Wait ticker initiated");
	anim = anim.append("text")
	      .attr("class", "tickers")
              .attr("dy", ".35em")
              .attr("text-anchor","middle")
              .attr("x", w/2)
              .style("fill-opacity", 0)
	      .style("font-size","0.5em")
	      .style("fill","#666666");
	
	function textUpdate(data){
	     	  
	  anim.attr("y",h/2 - 160)
		.text(data)
		.transition()
			.duration(750)
			.attr("y",h/2)
			.style("fill-opacity",1)
			.each("end",function() {
				anim.transition()
					.delay(1000)
					.duration(750)
					.attr("y",h/2+160)
					.style("fill-opacity",0);
				});
	}	
	
	console.log("Ticker rolling starts");
	
	textUpdate(strings[counter++]);
	   
	ticker = setInterval(function() {  textUpdate(strings[counter]); counter=(++counter)%strings.length;  }, 4000);

}

function initializeData(uid,accessToken,callback){
    console.log("Data fetching initialized");
    weAreWorkingAnimation();
    $.getJSON($SCRIPT_ROOT + '/_getProfile', { a: accessToken }, function(data) {
                console.log("User Id : " + data.id);
        me = data;
        $.getJSON($SCRIPT_ROOT + '/_getCloseFriends', { a: accessToken, b: me.id }, function(response) {
	        console.log("data fetched");
		ticker = window.clearInterval(ticker);
		d3.selectAll("#overlay").remove();
		console.log("tickers terminated");
                        friends = response;
                        init();
        });
    });
}


function User(person){
    var that=this;
    this.id = person.id;
    this.linkStats = person.score;
    this.fullName = person["name"];
    this.gender = person.gender;
    this.webLink = person.link;
    this.relationshipStatus = person.relationship_status;
    this.displayPic = person.picture;


    this.generateSprite = function (env,scale){
        scale = typeof scale !== 'undefined' ? scale : 1;
        var container = d3.select(env);
        var picMinAttr = this.displayPic.height <= this.displayPic.width ? "height" : "width";
        var picHeight,picWidth,minSize = 112*scale;
        if(picMinAttr == "height"){
             picHeight = minSize;
             picWidth = this.displayPic.width/this.displayPic.height * minSize;
        }
        else{
            picWidth = minSize;
            picHeight = this.displayPic.height/this.displayPic.width * minSize;
        }
        
        var thisSprite = container.append("g")
            .attr("id","spriteID" + that.id);	
			
        
        thisSprite.append("circle")
            .attr("class","spriteOuterCircle sprite" + that.id)
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",100*scale)
            .style("fill","none")
            .style("stroke","#3690ff")
            .style("stroke-width","10")
            .style("stroke-opacity",1)
            .style("filter","url(#spriteFilterOuterCircleBlur)");


        thisSprite.append("circle")
            .attr("class","spriteOuterCircle sprite" + that.id)
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",98 * scale)
            .style("fill","none")
            .style("stroke","#3690ff")
            .style("stroke-width","5");

        thisSprite.append("circle")
            .attr("class","spriteBackgroundCircle")
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",98 * scale)
            .style("fill","url(#spriteFilterBackgroundGradient)")
            .style("stroke","none")
            .style("fill-opacity","1");
 
        var infoPath = d3.svg.arc()
            .innerRadius(64 * scale)
			.outerRadius(64 * scale)
		    .startAngle(-1.5)
		    .endAngle(1.5);
     
	    thisSprite.append("path")
			.attr("id","spriteInfoCircle" + that.id)
			.style("fill", "brown")
			.style("stroke","brown")
			.style("stroke-width","2px")
			.attr("d", infoPath);
			

        thisSprite.append("text")
            .attr("class","spriteUserName")
            .attr("dy","-4px")
            .style("stroke","#666666")
            .style("font-size","0.8em")
            .style("font-weight","normal")
            .style("letter-spacing","1px")
            .append("textPath")
                .attr("text-anchor","middle")
                .attr("startOffset","25%")
                .attr("xlink:href","#spriteInfoCircle" + that.id)
                .text(function() { return that.fullName.length > 15 ? that.fullName.substring(0,13) + ".." : that.fullName; });
 
        thisSprite.append("circle")
            .attr("class","spritePhotoBackgroundCircle")
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",62 * scale)
            .style("fill","white");

        thisSprite.append("clipPath")
            .attr("class","spriteUserPhotoClipper sprite" + that.id)
            .attr("id","clipCircle" + that.id)
            .append("circle")
                .attr("cx",0)
                .attr("cy",0)
                .attr("r",minSize/2 - 0.1 * minSize)
                .attr("transform","translate(" + picWidth/2 + "," + picHeight/2 + ")");

        thisSprite.append("image")
            .attr("class","spriteUserPhoto")
            .attr("x",0)
            .attr("y",0)
            .attr("xlink:href",that.displayPic.url)
            .attr("width",picWidth)
            .attr("height",picHeight)
            .attr("clip-path","url(#clipCircle" + that.id + ")")
            .attr("transform","translate(-" + picWidth/2 + ",-" + picHeight/2 + ")")
            .on("mouseover",function(){
                    d3.selectAll(".sprite" + that.id).transition().attr("opacity",1); 
                    d3.selectAll(".link.user" + that.id).transition().duration(1000).style("stroke","#47a1ff").style("stroke-width","5px");
                })
            .on("mouseout",function(){
                    d3.selectAll(".sprite" + that.id).transition().attr("opacity",0);
                    d3.selectAll(".link.user" + that.id).transition().duration(1000).style("stroke","#9ecae1").style("stroke-width","1.5px");
                });
        
        d3.selectAll(".sprite" + that.id).attr("opacity",0);
    };
}

var init = function(){
    var elements;
    var nodes = new Array();

    ENV = d3.select("body").append("div").attr("id","svgContainer").append("svg").attr("height","100%").attr("width","100%");
    ENV.append("defs").append("filter").attr("id","spriteFilterOuterCircleBlur").append("feGaussianBlur").attr("stdDeviation","3.5");
    elements = ENV.select("defs").append("radialGradient").attr("id","spriteFilterBackgroundGradient").attr("cx","50%").attr("cy","50%").attr("fx","50%").attr("fy","50%").attr("r","100%");
    elements.append("stop").attr("stop-color","#e0e0e0").attr("stop-opacity","1").attr("offset","0%");
    elements.append("stop").attr("stop-color","#ffffff").attr("stop-opacity","1").attr("offset","60%");    
    scale = 0.8;
    
    me.userObject = new User(me);
    for(var i=0; i<friends.length ; i++){
        friends[i].userObject = new User(friends[i]);	
        nodes.push(friends[i]);            
    }

    me.children = friends;
    nodes.push(me);
    mainLayout = d3.layout.force()
        .on("tick", tick)
        .charge(-2500)
        .alpha(0.1)
        .size([w, h]);    
    
    update(ENV,nodes);
}

function update(env,nodes) {

    var links = d3.layout.tree().links(nodes);
    
    var linkScale = d3.scale.linear().domain([0,h/2]).range([220*scale,h/2]);

  // Restart the force layout.
  mainLayout
      .nodes(nodes)
      .links(links)
	  .linkDistance(function(d,i) { var dis = linkScale((h/2)*(1-i/nodes.length)) - (2 * margins); console.log(d.name + "'s Score : " + dis); return dis; } )
      .start();
 
  // Update the links
  link = env.selectAll("line.link")
      .data(links, function(d) { return d.target.id; });
 
  // Enter any new links.
  link.enter().insert("svg:line", ".node")
      .attr("class", function(d) { return "link user" + d.target.id + " user" + d.source.id;})
      .attr("x1", function(d) { return d.source.id == me.id ? w/2 : d.source.x; })
      .attr("y1", function(d) { return d.source.id == me.id ? h/2 : d.source.y; })
      .attr("x2", function(d) { return Math.max(100*scale,Math.min(w - (100*scale), d.target.x)); })
      .attr("y2", function(d) { return Math.max(100*scale,Math.min(h - (100*scale), d.target.y)); })
      .style("stroke","#9ecae1")
      .style("stroke-width","1.5px");
 
  // Exit any old links.
  link.exit().remove();
 
  // Update the nodes
  node = env.selectAll(".userSprite")
      .data(nodes, function(d) {return d.id; });
 
  // Enter any new nodes.
  node.enter().append("g")
      .attr("class","userSprite")
      .attr("transform", function(d) { d.userObject.generateSprite(this,scale); return d.id == me.id ? "translate(" + w/2 + "," + h/2 + ")"  : 
                                        "translate(" + Math.max(100*scale,Math.min(w - (100*scale), d.x)) + "," + Math.max(100*scale,Math.min(h - (100*scale), d.y)) + ")"; })
      .call(mainLayout.drag);
 
  // Exit any old nodes.
  node.exit().remove();
  
  d3.selectAll(".sprite" + me.id).transition().duration(3000).attr("opacity",1).each("end",function(){
                                    d3.selectAll(".sprite" + me.id).transition().delay(5000).duration(3000).attr("opacity",0)});                
    
}

function tick() {
  link.attr("x2", function(d) { return Math.max(100*scale,Math.min(w - (100*scale), d.target.x)); })
      .attr("y2", function(d) { return Math.max(100*scale,Math.min(h - (100*scale), d.target.y)); });
 
  node.attr("transform", function(d) { return d.id == me.id ? "translate(" + w/2 + "," + h/2 + ")"  : 
                                        "translate(" + Math.max(100*scale,Math.min(w - (100*scale), d.x)) + "," + Math.max(100*scale,Math.min(h - (100*scale), d.y)) + ")"; });
}



