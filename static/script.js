const imgPreview = document.getElementById('img-preview')
const imgUploader  = document.getElementById('img-uploader')
const imageUploadbar = document.getElementById('img-upload-bar');
const url = document.getElementById('url')

const CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/estefany/image/upload';
const cloudinary_code = 'akynwxvu';

imgUploader.addEventListener('change', async (event) =>{
	const file = event.target.files[0];
	
	const formData = new FormData()
	formData.append('file', file)
	formData.append('upload_preset', cloudinary_code)

	const res = await axios.post(CLOUDINARY_URL, formData, {
		headers: {
			'content-type': 'multipart/form-data'
		},

		onUploadProgress (event) {
			let progress = Math.round((event.loaded * 100.0) / event.total);
			console.log(progress);
			imageUploadbar.setAttribute('value', progress);
		}

	});

	console.log(res);
	imgPreview.src = res.data.secure_url;
	url.value = imgPreview.src
	
});

const videoPreview = document.getElementById('video-preview')
const videoUploader  = document.getElementById('video-uploader')
const videoUploadbar = document.getElementById('video-upload-bar');
const urlVideo = document.getElementById('urlV')

const CLOUDINARY_URL1 = 'https://api.cloudinary.com/v1_1/estefany/video/upload';
const cloudinary_code1 = 'akynwxvu';

videoUploader.addEventListener('change', async (event) =>{
	const file1 = event.target.files[0];
	
	const formData = new FormData()
	formData.append('file', file1)
	formData.append('upload_preset', cloudinary_code1)

	const res = await axios.post(CLOUDINARY_URL1, formData, {
		headers: {
			'content-type': 'multipart/form-data'
		},

		onUploadProgress (event) {
			let progress = Math.round((event.loaded * 100.0) / event.total);
			console.log(progress);
			videoUploadbar.setAttribute('value', progress);
		}

	});

	console.log(res);
	videoPreview.src = res.data.secure_url
	urlVideo.value = videoPreview.src
	
});

function likes(id){
	parametrs = {
	  id : id
	}
	$.getJSON("/likes?id=" + id, function(data){
	  if(data["me_gusta"] == false){
		$("#cont").text(parseInt($("#cont").text()) - 1);
		$("#corazon").css("color", "white");
	  }
	  if(data["me_gusta"] == true){
		$("#cont").text(parseInt($("#cont").text()) + 1);
		$("#corazon").css("color", "#e14eca");
	  }
	});
  };

  $("#btn_buscar").ready(function(){
    $('#btn_buscar').click(function(){
        
        let q = $("#search").val();
        console.log(q);

        if (q){
            $.getJSON("/search?q="+q, function(data){
                $("#coreos").empty();
                mostrarInfo(data);
                $("#search").val("");
                q = null;
            });
        };
        
    });
});


function mostrarInfo(data){
    for (let i = 0; i < data.length; i++) {
         
        var div = document.createElement("div");
        div.className = "card mt-2 mb-0 mr-2 ml-2";

        var titulo = document.createElement("h5");
		titulo.className = "card-title";
        titulo.innerHTML = data[i].titulo;
        div.appendChild(titulo);

        var desc = document.createElement("p");
        desc.innerHTML = data[i].descripcion;
        div.appendChild(desc);

		var link = document.createElement("a");
		link.className = "boton p-0 m-0";
        link.addEventListener('click', function(){
            redirect(data[i].pid);
        });

        var img = document.createElement("img");            
        img.src = data[i].portada;
        img.className = "img-coreo";
        img.alt = "imagen";
        link.appendChild(img);
     
        document.getElementById("coreo").appendChild(div);
    };
};

$(document).ready(function(){
    for(let i = 1; i <= 10; i++){
        $("#rit_"+i).click(function(){
            
            $.getJSON("/search?rit_id="+i, function(data){
                $("#coreo").empty();
                mostrarInfo(data);
                $("#search").val("");
            });
        });

        $("#rit_"+i).mouseover(function(){
            $("#rit_"+i).css("color","rgb(38, 228, 38)");
        });

        $("#cat_"+i).mouseout(function(){
            $("#cat_"+i).css("color","white");
        });
    };
});

function redirect(id){
    window.location.href = "coreografia?id=" + id;
};



