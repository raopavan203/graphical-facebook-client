var ENV,layoutContainer,debug;
var mainLayout;
var w = window.innerWidth,
    h = window.innerHeight;
var link,node;
var minLinkDistance=0,scale=1;
var margins = 10,padding = 20;
var ticker,counter,showingProfile = false;
var friends,me,nodes;
var strings = ["We Are Working.","Please wait while we fetch your closest friends","Working","Working.","Working..","Working...","Still Working",
               "We are really sorry!!","We will be faster next time","Almost done","really almost done","just a few more moments",
    	       "We will make sure, you don't regret the wait","Yep! It's that good","About to be done","Do let us know, how it is",
	           "We are building something really from scratch","Your likes","Your posts","Your messages","Your Tags",
	           "These things tell us who is close to you","It's all you","You'll see",":)",":D",":p",";)",";p","That was something","!!!",
               "We will be there","Don't worry","You can brew yourself a cup of coffee","We will keep track of thing while this is still working",
               "Its probably your first time","So we are building your profile from scratch",":D"];

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
	me.userStatus = me.status;
        $.getJSON($SCRIPT_ROOT + '/_getCloseFriends', { a: accessToken, b: me.id }, function(response) {
	        console.log("data fetched");
		ticker = window.clearInterval(ticker);
		d3.selectAll("#overlay").remove();
		console.log("tickers terminated");
                friends = response;

	        for(var i=0; i <friends.length ; i++)
		      friends[i].userStatus = friends[i].status;

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
    this.userStatus = person.userStatus;
    this.radius = 100;
    this.theater = new Object();
    this.theater.data = new Array();
    
    this.generateTheater = function(container) {

        function cameraRoll(){
            var roll = container.append("g")
                        .attr("id","cameraRoll");

            function addPics(){
                
                var lastx = 0;
                
                var pics = d3.select("#cameraRoll").select("#picsContainer");
                
                var clip = pics.selectAll(".picClipper")
                            .data(that.theater.data,function(d){ return d.id; });
            
                var images = pics.selectAll("image")
                            .data(that.theater.data,function(d){  return d.id; });
                            
                var rects = pics.selectAll("rect");
                rects[0].forEach(function(d) { var x = parseFloat(d3.select(d).attr("x")); lastx = lastx < x ? x : lastx;});
                if(lastx != 0) lastx -= 20;
                console.log("lastx " + lastx);
                
                clip.enter().append("clipPath")
                            .attr("id",function(d){ return "picClip" + d.id; })
                            .attr("class","picClipper")
                            .append("rect")
                                .attr("x", function(d,i) { return (i*110 + 25) + lastx; })
                                .attr("y" , h-85)
                                .attr("width", 100)
                                .attr("height" , 75);
            
                
                            
                images.enter()
                    .append("image")
                        .attr("height", function(d) { return d.height;})
                        .attr("width", function(d) { return d.width; })
                        .attr("x", function(d,i) {return (((i * 110) + 25) - (d.width - 100)/2) + lastx; })
                        .attr("y", h - 85)
                        .attr("xlink:href", function(d) { return d.thumbnail; })
                        .attr("preserveAspectRatio","none")	
                        .attr("clip-path", function(d) { return "url(#picClip" + d.id + ")";});
            }
            
                    
            function fetchNextBatch(){
                if(that.theater.next !== undefined)
                $.getJSON($SCRIPT_ROOT + '/_getData', { a: accessToken, b: that.id, c: "photos.limit(25).until(" + that.theater.next + ")" }, function(response){
                console.log("Fetched next Batch");
                
                var arrayLength = response.photos.data.length;
                var height,width,next;
                                
                for(var i = 0 ; i < arrayLength ; i++){
                    var pic = new Object();
                    pic.id = response.photos.data[i].id;
                    pic.from = response.photos.data[i].from;
                    pic.thumbnail = response.photos.data[i].picture;
                    pic.full = response.photos.data[i].source;
                    pic.height = response.photos.data[i].height;
                    pic.width = response.photos.data[i].width;
                    pic.createdTime = response.photos.data[i].created_time;
                    pic.comments = response.photos.data[i].comments != undefined ? response.photos.data[i].comments.data : undefined;
                    if(pic.width >= pic.height){
                        height = 75;
                        width = pic.width/pic.height * height;
                        if(width < 100)                                //Not Optimized. Stretches out thumbnails(unwanted). To do : optimize to preserve aspect ratio
                            width = 100;
                    } else {
                        width = 100;
                        height = pic.height/pic.width * width;
                        if(height < 75)                                //Not Optimized. Stretches out thumbnails(unwanted). To do : optimize to preserve aspect ratio
                            height = 75;
                    }
                    pic.height = height;
                    pic.width = width;

                    that.theater.data.push(pic);
                }
                
                next = response.photos.paging.next.split("&")[2].split("=")[1];
                that.theater.next = next;
                addPics();
            });
            }
        
            
            function forwardRoll(){
                var lastx = 0;
                
                var pics = d3.select("#cameraRoll").select("#picsContainer");                                
                
                var clip = pics.selectAll("rect")
                            .data(that.theater.data);
                
                clip.transition().attr("x",function(d) { return parseFloat(d3.select(this).attr("x")) - 110; });
                
                var images = pics.selectAll("image")
                                .data(that.theater.data);
                                
                images.transition().attr("x",function(d) { var inc = parseFloat(d3.select(this).attr("x")) - 110; lastx = inc > lastx ? inc : lastx; return inc;  });
            
                if(lastx <= (w + 720) && lastx > (w + 610))
                    fetchNextBatch();
                    
                if(lastx < (w - 100))
                    reverseRoll();
            }
            
            function reverseRoll(){
                var firstx = 0;
                
                var pics = d3.select("#cameraRoll").select("#picsContainer");                                
                
                var clip = pics.selectAll("rect")
                            .data(that.theater.data);
                
                clip.transition().attr("x",function(d) { return parseFloat(d3.select(this).attr("x")) + 110; });
                
                var images = pics.selectAll("image")
                                .data(that.theater.data);
                                
                images.transition().attr("x",function(d) { var dec = parseFloat(d3.select(this).attr("x")) + 110; firstx = dec < firstx ? dec : firstx; return dec; });
            
                if(firstx > 100)
                    forwardRoll();
            
            }            
            

            roll.append("rect")
                .attr("x",0)
                .attr("y", h-87)
                .attr("height",79)
                .attr("width",w)
                .style("fill","rgb(255,255,255)")
                .style("filter","url(#spriteFilterOuterCircleBlur)");            
            
            roll.append("rect")
                .attr("x",0)
                .attr("y", h-87)
                .attr("height",79)
                .attr("width",w)
                .style("fill","rgb(0,0,0)");
            
            roll.append("g")
                .attr("id","picsContainer");

         
            roll.append("rect")
                .attr("x",0)
                .attr("y",h - 90)
                .attr("width",30)
                .attr("height",85)
                .style("fill","rgba(0,0,0,0.8)")
                .on("click",function() { reverseRoll(); });
                        
            roll.append("rect")
                 .attr("x", w - 30)
                 .attr("y",h - 90)
                 .attr("width",30)
                 .attr("height",85)
                 .style("fill","rgba(0,0,0,0.8)")
                 .on("click", function() { forwardRoll(); } );
                        
            roll.append("path")
                 .attr("d","M 5 " + (h-50) + " l 5 5 l 0 -10 Z")
                 .style("fill","rgba(255,255,255,0.8)");
                        
            roll.append("path")
                 .attr("d","M " + (w-5) + " " + (h-50) + " l -5 5 l 0 -10 Z")
                 .style("fill","rgba(255,255,255,0.8)");  
           
            addPics();
                

        }
        
        if(that.theater.data.length == 0)
            $.getJSON($SCRIPT_ROOT + '/_getData', { a: accessToken, b: that.id, c:"photos" }, function(response){

                var arrayLength = response.photos.data.length;
                var height,width,next;
                                
                for(var i = 0 ; i < arrayLength ; i++){
                    var pic = new Object();
                    pic.id = response.photos.data[i].id;
                    pic.from = response.photos.data[i].from;
                    pic.thumbnail = response.photos.data[i].picture;
                    pic.full = response.photos.data[i].source;
                    pic.height = response.photos.data[i].height;
                    pic.width = response.photos.data[i].width;
                    pic.createdTime = response.photos.data[i].created_time;
                    pic.comments = response.photos.data[i].comments != undefined ? response.photos.data[i].comments.data : undefined;
                    if(pic.width >= pic.height){
                        height = 75;
                        width = pic.width/pic.height * height;
                        if(width < 100)                                //Not Optimized. Stretches out thumbnails(unwanted). To do : optimize to preserve aspect ratio
                            width = 100;
                    } else {
                        width = 100;
                        height = pic.height/pic.width * width;
                        if(height < 75)                                //Not Optimized. Stretches out thumbnails(unwanted). To do : optimize to preserve aspect ratio
                            height = 75;
                    }
                    pic.height = height;
                    pic.width = width;

                    that.theater.data.push(pic);
                }
                
                next = response.photos.paging.next.split("&")[2].split("=")[1];
                that.theater.next = next;
                    
                
                cameraRoll();        
            });
        else
            cameraRoll();
    }
    
     
    this.generateProfileLayout = function(){
	
	that.removeStatus();	
	
	showingProfile = true;

	mainLayout.stop();

	d3.selectAll(".sprite" + that.id).transition().attr("opacity",1);

	layoutContainer.transition()
            .attr("transform","translate(" + (w/2 - that.x) + "," + (h/2 - that.y) + ")");
                
        var profileContainer = ENV.append("g")
                                .attr("id","profileLayout");
        
        profileContainer.append("rect")
            .attr("x",0)
            .attr("y",0)
            .attr("height",h)
            .attr("width",w)
            .attr("mask","url(#profileMask)")
            .style("fill","none")
            .transition()
                .style("fill","rgba(0,0,0,0.8)");
                
        profileContainer.append("circle")
            .attr("cx",w/2)
            .attr("cy",h/2)
            .attr("r", 100*scale)
            .style("fill","rgba(0,0,0,0)")
            .on("click",function(){ that.destroyProfile(); });
            
        that.generateTheater(profileContainer);
    }
    
    this.destroyProfile = function(){
	    showingProfile = false;
        d3.selectAll(".sprite" + that.id).transition().attr("opacity",0); 
        d3.select("#profileLayout").remove();
        layoutContainer.transition()
            .attr("transform","");
    }
    
    this.removeStatus = function(){
        d3.selectAll(".spriteUserStatus").remove();
    }
    
    this.showStatus = function(){
    	var width = 300;	
    	var height = width/2;
    	
    	var topSpaceAvailable = true;
    	var leftRightAlign = "middle";
    	
    	if((that.y - that.radius*scale) < height + 20)                              //Decides whether to generate bubble on top or bottom of sprite
    	    topSpaceAvailable = false;
    	    
    	if((that.x - that.radius*scale) < 200)                              //Decides bubble alignment. Default : middle. On space availability : left or right
    	    leftRightAlign = "right";
    	else if((w-that.x - that.radius * scale) < 200)
    	    leftRightAlign = "left";
    	    
	    var statusObject = ENV.append("g")
		    .attr("class","spriteUserStatus")
		    .attr("transform","translate(" + that.x + "," + (topSpaceAvailable ? (that.y - that.radius * scale) : (that.y + that.radius * scale)) + ")");
		    
		statusObject.append("path")
           .attr("class","spriteUserStatusBackground")
           .attr("d",function(){
                var rightSideLength,leftSideLength;
                if(leftRightAlign === "middle")
                    leftSideLength = rightSideLength = width/2 - 5;
                else if(leftRightAlign === "right")
                    leftSideLength = width - 10 - (rightSideLength = width - that.radius * scale - 5);
                else
                    leftSideLength = width - 10 - (rightSideLength = that.radius * scale - 5);  
                    
                if(topSpaceAvailable)
                    return  "M 0 0 l 5 -10 l " + rightSideLength + " 0 l 0 -" + height + " l -" + width + " 0 l 0 " + height + " l " + leftSideLength + " 0 Z";
                else
                    return  "M 0 0 l 5 10 l " + rightSideLength + " 0 l 0 " + height + " l -" + width + " 0 l 0 -" + height + " l " + leftSideLength + " 0 Z";
                })
           .style("fill","white");
    
         var statusContainer = statusObject
                .append("foreignObject")
                    .attr("x",function(){
                        if(leftRightAlign === "middle")
                            return -(width/2 - 5);
                        else if(leftRightAlign === "left")
                            return -(width - that.radius * scale - 5);
                        else
                            return -(that.radius * scale - 5);
                        })
                    .attr("y",topSpaceAvailable ? -(height - 5) : 15)
                    .attr("width","290")
		    .attr("height",height - 10);
                    
          statusContainer.append("xhtml:div")
                    .attr("class","spriteUserStatus")
                    .attr("id","status" + that.id)
                    .style("width","290px")
                        .html((that.userStatus.message != undefined ? that.userStatus.message : "NA") +
			      "<p>" + 
			      (that.userStatus.updated_time != undefined ? that.userStatus.updated_time : "NA"));


    }

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
	    .on("click",function() {
			that.generateProfileLayout();
		})
	    .on("mouseover",function(){
                    d3.selectAll(".sprite" + that.id).transition().attr("opacity",1); 
                    d3.selectAll(".link.user" + that.id).transition().duration(1000).style("stroke","#47a1ff").style("stroke-width","5px");
 		    that.showStatus();
                })
            .on("mouseout",function(){
                    if(!showingProfile)
			d3.selectAll(".sprite" + that.id).transition().attr("opacity",0);
                    d3.selectAll(".link.user" + that.id).transition().duration(1000).style("stroke","#9ecae1").style("stroke-width","1.5px");
                    that.removeStatus();
                });
        
        d3.selectAll(".sprite" + that.id).attr("opacity",0);
    };
}


var init = function(){
    var elements;
    scale = 0.6;

    nodes = new Array();

    ENV = d3.select("body")
		.append("div")
			.attr("id","svgContainer")
			.append("svg")
				.attr("height","100%")
				.attr("width","100%");
					
    layoutContainer = ENV.append("g");
						

    var defs = ENV.append("defs");
	
	defs.append("filter")
			.attr("id","spriteFilterOuterCircleBlur")
				.append("feGaussianBlur")
					.attr("stdDeviation","3.5");

    elements = defs
        		.append("radialGradient")
		        	.attr("id","spriteFilterBackgroundGradient")
		        	.attr("cx","50%")
		        	.attr("cy","50%")
		        	.attr("fx","50%")
		        	.attr("fy","50%")
		        	.attr("r","100%");

    elements.append("stop")
		.attr("stop-color","#e0e0e0")
		.attr("stop-opacity","1")
		.attr("offset","0%");

    elements.append("stop")
		.attr("stop-color","#ffffff")
		.attr("stop-opacity","1")
		.attr("offset","60%");    

    elements = defs.append("mask")
        .attr("id","profileMask")
        .attr("maskUnits","userSpaceOnUse")
        .attr("x","0%")
        .attr("y","0%")
        .attr("width",w)
        .attr("height",h);
        
    elements.append("rect")
        .attr("x","0%")
        .attr("y","0%")
        .attr("height","100%")
        .attr("width","100%")
        .style("fill","rgba(255,255,255,1)");
        
    elements.append("circle")
        .attr("cx",w/2)
        .attr("cy",h/2)
        .attr("r", (scale*100 + 10))
        .style("fill","rgba(0,0,0,1)");
    
    elements = defs.append("linearGradient")
        .attr("id","linearDarkToTransGradient");
        
    elements.append("stop")
        .attr("offset",0)
        .style("stop-color","#000000")
        .style("stop-opacity",0.9);
        
    elements.append("stop")
        .attr("offset",1)
        .style("stop-color","#000000")
        .style("stop-opacity",0);
        
    
    elements=defs.append("linearGradient")
        .attr("id","cameraRollLeftTabGradient")
        .attr("xlink:href","#linearDarkToTransGradient")
        .attr("x1",0)
        .attr("y1",0)
        .attr("x2",30)
        .attr("y2",0)
        .attr("gradientUnits","userSpaceOnUse");
   
    elements=defs.append("linearGradient")
        .attr("id","cameraRollRightTabGradient")
        .attr("xlink:href","#linearDarkToTransGradient")
        .attr("x1","100%")
        .attr("y1","0%")
        .attr("x2","0%")
        .attr("y2","0%")
        .attr("gradientUnits","userSpaceOnUse");
   
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
	.alpha(0.2)
	.gravity(0)
        .size([w, h]);    
    
    update(layoutContainer,nodes);
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
      .attr("x2", function(d) { return d.target.userObject.x = d.target.x = Math.max(100*scale,Math.min(w - (100*scale), d.target.x));})
      .attr("y2", function(d) { return d.target.userObject.x = d.target.y = Math.max(100*scale,Math.min(w - (100*scale), d.target.y));})
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
      .attr("transform", function(d) {
                d.userObject.generateSprite(this,scale);
                if( d.id == me.id){
                        d.userObject.x = d.x = w/2;
                        d.userObject.y = d.y = h/2;
		}

                return "translate(" + d.x + "," + d.y + ")";  
        })
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

  node.forEach(function(d){ 
		if(d.y < (h/2))
			d.y = (d.y + d.y*2/h * e.alpha*4);
		else
			d.y = (d.y - d.y*2/h * e.alpha*4);  
	});
	
  node
       .attr("transform", function(d) {
		if(d.id == me.id){
			d.userObject.x = d.x = w/2;
			d.userObject.y = d.y = h/2;
		} else {
			d.userObject.x = d.x = Math.max(100*scale,Math.min(w - (100*scale), d.x));
			d.userObject.y = d.y = Math.max(100*scale,Math.min(h - (100*scale), d.y));
		}
		return "translate(" + d.x + "," + d.y + ")"; 
	});

  link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
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

    	  l = ((l - r) / l) * 0.5;
          inode.x -= x *= l;
          inode.y -= y *= l;
          quad.point.x += x;
          quad.point.y += y;
	}
      }
      return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
   };
}

$(window).resize(function() {
  //resize just happened, pixels changed
  var newScale = h<w ? h/window.innerHeight : w/window.innerWidth;
  scale *= newScale;
  ENV.attr("transform","scale("+newScale+")");

  w = window.innerWidth;
  h = window.innerHeight;
  
  if(!showingProfile)
      mainLayout.resume(); 
});
