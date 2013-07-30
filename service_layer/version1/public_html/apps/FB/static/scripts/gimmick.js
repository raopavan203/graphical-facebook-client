var ENV;
var mainLayout;
var w = window.innerWidth,
    h = window.innerHeight;
var link,node;
var minLinkDistance=0,scale=1;
var margins = 10,padding = 20;
var ticker,counter;
var friends,me,nodes;
var strings = ["We Are Working.","Please wait while we fetch your closest friends","Working","Working.","Working..","Working...","Still Working",
               "We are really sorry!!","This won't happen next time","Almost done","really almost done","just a few more moments",
	       "We will make sure, you don't regret the wait","Yep! It's that good","About to be done","Do let us know, how it is",
	       "We are building something really from scratch","Your likes","Your posts","Your messages","Your Tags",
	       "These things tell us who is close to you","It's all you","You'll see",":)",":D",":p",";)",";p","That was something","!!!",
               "We will be there","Don't worry","You can brew yourself a cup of coffee","We will keep track of thing while this is still working",
               "Its probably your first time","So we are building your profile from scratch",":D"];


var server = new Object();									//Dummy server object

server.restCall = function(restString,callback){
/*	var restUID,restAccessToken,restReq,restKeyValue;
	var restVariables = restString.split("&");
	
	for(var i=0; i<restVariables.length ; i++){
		restKeyValue = restVariables[i].split("=");
		if(restKeyValue[0] === "uid")
			restUID = restKeyValue[1];
		else if(restKeyValue[0] === "access_token")
			restAccessToken = restKeyValue[1];
		else if(restKeyValue[0] === "q")
			restReq = restKeyValue[1];
	}
	
	if(restUID == undefined || restAccessToken == undefined || restReq == undefined){
		console.log("undefined values in AJAX call.");
		console.log("UID : " + restUID);
		console.log("Access Token : " + restAccessToken);
		console.log("Request : " + restReq);
		callback({"Error" : "Undefined Values Present"});
	}
	else{
*/		FB.api("/" + restString,function(response){
			console.log("Response : " + response);
			callback(response);
		});
//	}
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

function statusBubble(user){
	var statusObject = ENV.append("g")
		.attr("class","spriteUserStatus")
                                        .attr("transform","translate(" + that.x + "," + (that.y - that.radius) + ")");

                                statusObject.append("path")
                                        .attr("class","spriteUserStatusBackground")
                                        .attr("d","M 0 0 l 10 -15 q 4 -6 10 -6 l 175 0 q 5 0 5 -5 l 0 -" + 200 + " q 0 -5 -5 -5 " +
                                                "l -390 0 q -5 0 -5 5 l 0 " + 200 + " q 0 5 5 5 l 175 0 q 6 0 10 6 Z")
                                        .style("fill","white");

                                var statusContainer = statusObject
                                                .append("foreignObject")
                                                .attr("x","-200")
                                                .attr("width","400");

                                var statusBody = statusContainer
                                        .append("xhtml:div")
                                        .attr("class","spriteUserStatus")
                                        .attr("id","status" + that.id)
                                        .style("width","380px")
                                                .html("Fetching Status");

                                var divHeight = $("#status" + that.id).height();

                                divHeight = 200;

                                statusContainer
                                        .attr("height",divHeight + 10)
                                        .attr("y", -divHeight + 50);

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
    this.radius = 100;


    this.generateSprite = function (env,scale){
        scale = typeof scale !== 'undefined' ? scale : 1;
        var container = d3.select(env);
        var picMinAttr = this.displayPic.height <= this.displayPic.width ? "height" : "width";
        var picHeight,picWidth,minSize = 112*scale;
        picHeight = minSize;
        picWidth = this.displayPic.width/this.displayPic.height * minSize;
	picWidth = (picWidth >= minSize) ? picWidth : minSize;
  
        var thisSprite = container.append("g")
            .attr("id","spriteID" + that.id);	
			
        
        thisSprite.append("circle")
            .attr("class","spriteOuterCircle sprite" + that.id)
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",that.radius*scale)
            .style("fill","none")
            .style("stroke","#3690ff")
            .style("stroke-width","10")
            .style("stroke-opacity",1)
            .style("filter","url(#spriteFilterOuterCircleBlur)");


        thisSprite.append("circle")
            .attr("class","spriteOuterCircle sprite" + that.id)
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",(that.radius-2) * scale)
            .style("fill","none")
            .style("stroke","#3690ff")
            .style("stroke-width","5");

        thisSprite.append("circle")
            .attr("class","spriteBackgroundCircle")
            .attr("cx",0)
            .attr("cy",0)
            .attr("r",(that.radius-2) * scale)
            .style("fill","url(#spriteFilterBackgroundGradient)")
            .style("stroke","none")
            .style("fill-opacity","1");
 
        var infoPath = d3.svg.arc()
            .innerRadius((that.radius-36) * scale)
			.outerRadius((that.radius - 36) * scale)
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
            .attr("r",(that.radius - 38) * scale)
            .style("fill","white");

        thisSprite.append("clipPath")
            .attr("class","spriteUserPhotoClipper sprite" + that.id)
            .attr("id","clipCircle" + that.id)
            .append("circle")
                .attr("cx",0)
                .attr("cy",0)
                .attr("r",minSize/2)
                .attr("transform","translate(" + minSize/2 + "," + picHeight/2 + ")");

        thisSprite.append("image")
            .attr("class","spriteUserPhoto")
            .attr("x",0)
            .attr("y",0)
            .attr("xlink:href",that.displayPic.url)
            .attr("width",picWidth)
            .attr("height",picHeight)
	    .attr("preserveAspectRatio","none")	
            .attr("clip-path","url(#clipCircle" + that.id + ")")
            .attr("transform","translate(-" + minSize/2 + ",-" + picHeight/2 + ")")
            .on("mouseover",function(){
                    d3.selectAll(".sprite" + that.id).transition().attr("opacity",1); 
                    d3.selectAll(".link.user" + that.id).transition().duration(1000).style("stroke","#47a1ff").style("stroke-width","5px");
		    
		    if(that.x === undefined || that.y === undefined){
			for(var i=0; i < nodes.length;i++){
				if(nodes[i].id == that.id){
					that.x = nodes[i].x;
					that.y = nodes[i].y;
				}
			}
		    }	 
		   	
		    var statusObject = ENV.append("g")
                                        .attr("class","spriteUserStatus")
                                        .attr("transform","translate(" + that.x + "," + (that.y - that.radius) + ")");

                                statusObject.append("path")
                                        .attr("class","spriteUserStatusBackground")
                                        .attr("d","M 0 0 l 10 -15 q 4 -6 10 -6 l 175 0 q 5 0 5 -5 l 0 -" + 200 + " q 0 -5 -5 -5 " +
                                                "l -390 0 q -5 0 -5 5 l 0 " + 200 + " q 0 5 5 5 l 175 0 q 6 0 10 6 Z")
                                        .style("fill","white");

                                var statusContainer = statusObject
                                                .append("foreignObject")
                                                .attr("x","-200")
                                                .attr("width","400");

                                var statusBody = statusContainer
                                        .append("xhtml:div")
                                        .attr("class","spriteUserStatus")
                                        .attr("id","status" + that.id)
                                        .style("width","380px")
                                                .html("Fetching Status");

                                var divHeight = $("#status" + that.id).height();

                                divHeight = 200;

                                statusContainer
                                        .attr("height",divHeight + 10)
                                        .attr("y", -divHeight + 50);

				if(that.userStatus === undefined)
				    server.restCall(that.id+"/statuses",function(response){
				
					that.userStatus = response.data[0];
					statusBody.html(that.userStatus.message + "<p><p>" + that.userStatus.updated_time);

				}); 
				else{
					statusBody.html(that.userStatus.message + "<p><p>" + that.userStatus.updated_time);
				}
                })
            .on("mouseout",function(){
                    d3.selectAll(".sprite" + that.id).transition().attr("opacity",0);
                    d3.selectAll(".link.user" + that.id).transition().duration(1000).style("stroke","#9ecae1").style("stroke-width","1.5px");
		    d3.selectAll(".spriteUserStatus").remove();
                });
        
        d3.selectAll(".sprite" + that.id).attr("opacity",0);
    };
}


var init = function(){
    var elements;
    nodes = new Array();

    ENV = d3.select("body").append("div").attr("id","svgContainer").append("svg").attr("height","100%").attr("width","100%");
    ENV.append("defs").append("filter").attr("id","spriteFilterOuterCircleBlur").append("feGaussianBlur").attr("stdDeviation","3.5");
    elements = ENV.select("defs").append("radialGradient").attr("id","spriteFilterBackgroundGradient").attr("cx","50%").attr("cy","50%").attr("fx","50%").attr("fy","50%").attr("r","100%");
    elements.append("stop").attr("stop-color","#e0e0e0").attr("stop-opacity","1").attr("offset","0%");
    elements.append("stop").attr("stop-color","#ffffff").attr("stop-opacity","1").attr("offset","60%");    
    scale = 0.6;
    
    me.userObject = new User(me);
    for(var i=0; i<friends.length ; i++){
        friends[i].userObject = new User(friends[i]);	
        nodes.push(friends[i]);            
    }

    me.children = friends;
    nodes.push(me);
    mainLayout = d3.layout.force()
        .on("tick", tick)
        .charge(-4000)
	.alpha(0.1)
	.gravity(0)
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
	  .linkDistance(function(d,i) { var dis = linkScale((h/2)*(1-i/nodes.length)) - (2 * margins);  return dis; } )
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

function tick(e) {
  var q = d3.geom.quadtree(nodes),i=0,n = nodes.length;

  while (++i < n) {
    q.visit(collide(nodes[i]));
  }

  node.forEach(function(d){ d.y = d.y < (h/2) ? d.y + d.y*2/h * e.alpha*4 : d.y - d.y*2/h * e.alpha*4;  
			});
	
  node
       .attr("transform", function(d) { return d.id == me.id ? "translate(" + (d.x = w/2) + "," + (d.y = h/2) + ")"  : 
                                        "translate(" + (d.x = Math.max(100*scale,Math.min(w - (100*scale), d.x))) + "," + (d.y=Math.max(100*scale,Math.min(h - (100*scale), d.y))) + ")"; });

  link.attr("x2", function(d) { return Math.max(100*scale,Math.min(w - (100*scale), d.target.x)); })
      .attr("y2", function(d) { return Math.max(100*scale,Math.min(h - (100*scale), d.target.y)); });
}



function collide(inode) {
    var r = inode.userObject.radius * scale + padding,
        nx1 = inode.x - r,
        nx2 = inode.x + r,
        ny1 = inode.y - r,
        ny2 = inode.y + r;
    return function(quad, x1, y1, x2, y2) {
	
      if (quad.point != undefined && quad.point != null && (quad.point.id != inode.id)) {
	var x = inode.x - quad.point.x,
            y = inode.y - quad.point.y,
            l = Math.sqrt(x * x + y * y),
            r = 2 * inode.userObject.radius * scale;

        if (l < r) {

    	  l = ((l - r) / l);
          inode.x -= x *= l;
          inode.y -= y *= l;
          quad.point.x += x;
          quad.point.y += y;
	}
      }
      return x1 > nx2
          || x2 < nx1
          || y1 > ny2
          || y2 < ny1;
   };
}
