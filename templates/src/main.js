// Author: 2017 Doron Goldfarb, doron.goldfarb@umweltbundesamt.at

import Vue from 'vue/dist/vue.js';
import * as Icon from 'vue-awesome';
import axios from 'axios';
import https from 'https';
import FileReader  from './FileReader.vue';

var Filereader = Vue.component('text-reader', FileReader);

var confirmmodal = Vue.component('confirmmodal',{
	props: ['message'],
	template: `\
		<transition name="modal">\
    <div class="modal-mask">\
      <div class="modal-wrapper">\
        <div class="modal-container">\
\
          <div class="modal-header">\
            <slot name="header">\
              Confirm deletion\
            </slot>\
          </div>\
\
          <div class="modal-body">\
            <slot name="body">\
          	<a>Really delete {{message.title}} ?</a> \
            </slot>\
          </div>\
\
          <div class="modal-footer">\
            <slot name="footer">\
              <button class="modal-default-button" @click="$emit('close')">Cancel</button>\
	      <button class="modal-default-button" @click="$emit('deletetemplate', message)">Delete</button>\
            </slot>\
          </div>\
        </div>\
      </div>\
    </div>\
  </transition>\
`
});


var aboutmodal = Vue.component('aboutmodal',{
	props: [],
	template: `\
  <transition name="modal">\
    <div class="modal-mask">\
      <div class="modal-wrapper">\
        <div class="modal-container">\
\
          <div class="modal-header">\
            <slot name="header">\
              About this service:
            </slot>\
          </div>\
\
          <div class="modal-body">\
            <slot name="body">\
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut interdum urna sed metus pretium cursus. Curabitur et euismod libero, et bibendum tortor. Phasellus ac volutpat nibh. Duis posuere velit sed pulvinar convallis. Donec ut felis efficitur, interdum erat in, volutpat massa. Morbi interdum odio ut blandit hendrerit. <br>
			  Sed aliquam maximus justo, at gravida dui porttitor maximus. In a arcu sit amet dui maximus vestibulum quis vitae turpis.\
            </slot>\
          </div>\
\
          <div class="modal-footer">\
            <slot name="footer">\
              <button class="modal-default-button" @click="$emit('close')">Ok</button>\
            </slot>\
          </div>\
        </div>\
      </div>\
    </div>\
  </transition>\
`
});


var modal = Vue.component('modal',{
	props: ['message', 'first', 'add', 'text2'],
	template: `\
		<transition name="modal">\
    <div class="modal-mask">\
      <div class="modal-wrapper">\
        <div class="modal-container" style="height: 700px; width: 1200px;">\
\
          <div v-if="this.first" class="modal-header">\
            <slot name="header">\
		Template registration	
            </slot>\
          </div>\
\
          <div style=" max-height: 600px; overflow-y:scroll; border: 1px black solid">
          <div class="modal-body">\
            <slot name="body">\
            <table>
		<tr>
			<td>
			<table>
				<tr>
				    <td>Title *</td>
				    <td><input v-model="message.title"></input></td>
				</tr>
				<tr>
				    <td>Subject *</td>
				    <td><input v-model="message.subject"></input></td>
				</tr>
				<tr>
				    <td>Description *</td>
				    <td><input v-model="message.description"></input></td>
				</tr>
				<tr>
				    <td>Type *</td>
				    <td><input v-model="message.type"></input></td>
				</tr>
				<tr>
				    <td>Coverage</td>
				    <td><input v-model="message.coverage"></input></td>
				</tr>
				<tr>
				    <td>Comment</td>
				    <td><input v-model="message.comment"></input></td>
				</tr>
				<tr>
				    <td>Creator</td>
				    <td><input v-model="message.creator"></input></td>
				</tr>
          		</table>
			</td>\
			<td>
				<textarea  style="resize: none" cols="80" rows="20" v-model="message.prov">@{{text2}}</textarea> 
			</td> \
		</tr>\
		<tr>
			<td></td>
			<td><table>
				<tr>
					<td><text-reader @load="message.prov=$event; text2=$event;"></text-reader></td>
					<td><div style="padding-right: 20px"><button class="modal-default-button" @click="$emit('renderprov', message.prov)">renderProv</button></div></td>
				</tr>
			</table></td>
		</tr>	
		<tr>
			<td colspan=2>
              			<div id="svg"></div> \
			</td> \
		</tr>
		</table>
            </slot>\
          </div>\
          <div style="padding-left: 20px; font-size: 70%">
              Fields marked with a * are required.
          </div>
          </div>

\
          <div class="modal-footer" id="button_footer">\
            <slot name="footer">\
              <div style="padding-right: 20px"><button class="modal-default-button" @click="$emit('close')">Cancel</button></div> \
	      <div v-if="this.add" style="padding-left: 150px"><button class="modal-default-button" @click="$emit('addtemplate', message)">Add</button></div>
	      <div v-if="!this.add & message.title!='' & message.subject!='' & message.description!='' & message.type!=''" style="padding-left: 150px">\
			<button class="modal-default-button" @click="$emit('changetemplate', message)">Update</button></div>
            </slot>\
          </div>\
        </div>\
      </div>\
    </div>\
  </transition>\
`
});



Vue.component('icon', Icon)

        var myList=Vue.component('template-item', {
          props: ['title', 'subject', 'description', 'type', 'coverage', 'comment', 'creator', 'created', 'modified', 'prov', 'provsvg', 
			'urlprovn','urlprovxml','urlprovjson','urlprovrdftrig','urlprovrdfxml','owner', 'jwt'],
	  mounted: function() {
		var svg = new DOMParser().parseFromString(this.provsvg, 'application/xml').documentElement;
		svg.style.width="100%";
		svg.style.height="100%";
		svg.style.maxheight="200px";
		//svg.style.position="absolute";
		//svg.style.background="yellow";
		console.log(this.$refs.canvas);
  		var el = this.$refs.canvas; 
		
		while (el.firstChild) {
		     console.log("REMOVING");
		    el.removeChild(el.firstChild);
		}
  		el.appendChild( el.ownerDocument.importNode(svg, true));
		el.style.maxheight="300px";
		el.style.height="300px";
		//el.style.height="100%";
		//el.style.width="50%";
		//el.style.height="300px";
	  }, 
					//<tr><td nowrap style="padding 50px 0"><b>Title:</b> {{ title }}</td></tr> \
					//<tr><td style="padding 50px 0"><b>Description:</b> <label style="max-width: 512px; word-wrap: break-word; cursor: default">{{ description }}</label></td></tr> \
					//<tr><td style="padding 50px 0"><b>Creator:</b> {{ creator }}</td></tr> \
					//<tr><td style="padding 50px 0"><b>Coverage:</b> {{ coverage }}</td></tr> \
					//<tr><td style="padding 50px 0"><b>Subject:</b> {{ subject }}</td></tr> \
					//<tr><td style="padding 50px 0"><b>Type:</b> {{ type }}</td></tr> \
					//<tr><td style="padding 50px 0"><b>Comment:</b> {{ comment }}</td></tr> \
          template: ` <tr> 
			<td style="border-bottom: 1px solid black; "> \
			    <table style="line-height: 1;  padding:0.5rem 0.5rem ! important;"> \
					<tr><td nowrap><b>Title:</b> {{ title }}</td></tr> \
					<tr><td><b>Description:</b> <label style="max-width: 512px; word-wrap: break-word; cursor: default">{{ description }}</label></td></tr> \
					<tr><td><b>Creator:</b> {{ creator }}</td></tr> \
					<tr><td><b>Coverage:</b> {{ coverage }}</td></tr> \
					<tr><td><b>Subject:</b> {{ subject }}</td></tr> \
					<tr><td><b>Type:</b> {{ type }}</td></tr> \
					<tr><td><b>Comment:</b> <label style="max-width: 512px; word-wrap: break-word; cursor: default">{{ comment }}</label></td></tr> \
					<tr><td><a :href="urlprovn">prov-n</a></td></tr> \
					<tr><td><a :href="urlprovxml">prov-xml</a></td></tr> \
					<tr><td><a :href="urlprovjson">prov-json</a></td></tr> \
					<tr><td><a :href="urlprovrdftrig">prov-o (TriG)</a></td></tr> \
					<tr><td><a :href="urlprovrdfxml">prov-o (rdf-xml)</a></td></tr> \
					<tr><td><b>Created:</b> {{ created }}</td></tr> \
					<tr><td><b>Modified:</b> {{ modified }}</td></tr> \
			    </table> \
			</td> \
			<td style="border-bottom: 1px solid black; "> \
				<div class="wrapper" style="width: 100%; height: 100%"> \
					<div class="container" style="height: 100%; margin: 0 auto;  position: relative;" id="canvas" ref="canvas"> \
					//<div class="container" style="width: 50%; margin: 0 auto; maxwidth: 300px; position: relative;" id="canvas" ref="canvas"> 
					</div> \
				</div> \
			</td>
            <td style="border-bottom: 1px solid black; " v-if='jwt'><button :disabled="owner==0" v-on:click="$emit(\'edit\')"><icon name="edit" style="color: #000000"></icon></button></td> \
            <td style="border-bottom: 1px solid black; " v-if='jwt'><button :disabled="owner==0" v-on:click="$emit(\'remove\')"><icon name="ban" style="color: #FF0000"></icon></button></td>
            <td style="border-bottom: 1px solid black; " v-if='!jwt'><button style="visibility: hidden;" :disabled="owner==0" v-on:click="$emit(\'edit\')"><icon name="edit" style="color: #000000"></icon></button></td> \
            <td style="border-bottom: 1px solid black; " v-if='!jwt'><button style="visibility: hidden;" :disabled="owner==0" v-on:click="$emit(\'remove\')"><icon name="ban" style="color: #FF0000"></icon></button></td> </tr> `
            /*<td><button style="invisiblebutton" :disabled="owner==0" v-on:click="$emit(\'edit\')"><icon name="edit" style="color: #000000"></icon></button></td> \
            <td><button style="invisiblebutton" :disabled="owner==0" v-on:click="$emit(\'remove\')"><icon name="ban" style="color: #FF0000"></icon></button></td> </tr>`*/
        });


	window.Vue=new Vue({
                el: '#template-list-example',
                  data: {
			text: "WHAT",
			provider: null,
			user: null,
			jwt: null,
			axiosInstance: null,
			curRep: null,
			showModal: false,
			showConfirmModal: false,
			showAboutModal: false,
			showAuth: false,
			showAdd: true,
			firstForm: true,
                    newText: '',
                    templates: [],
                    nextTemplateId: 4
                  },
		  mounted() {
			this.axiosInstance=axios.create({
				httpsAgent: new https.Agent({  
					rejectUnauthorized: false
				})
			});
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/getTemplateList",
						{},
						{ headers: this.createJwtHeaderData() }
						)
			.then( response => { 
				this.templates = response.data;
				console.log(response);
			})
			.catch(function(error) {console.log(error)});
			console.log(this.templates)
		  },
                  components: { FileReader : FileReader, myList : myList, modal : modal, confirmmodal : confirmmodal, aboutmodal : aboutmodal},
                  methods: {
		    createJwtHeaderData: function() {
			var headerdata={};
			if (this.jwt)
				headerdata = { Authorization : "Bearer " + this.jwt };
			return headerdata;
		    },
		    triggerLoginComplete: function () {
			console.log("hi there");
		    },
		    triggerLogout: function () {
			this.jwt=null;
			this.provider=null;
			this.user=null;
			window.location.reload(true);
			/*
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/getTemplateList",
						{},
						{ headers: this.createJwtHeaderData() }
						)
			.then( response => { 
				this.templates = response.data;
				console.log(response); 
			})
			.catch(function(error) {console.log(error)});
			*/
		    },
		    convertProv: function (data) {
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/renderProvFile", 
						{'provfile':data},
						{ headers: this.createJwtHeaderData()})
			.then( response => {
				console.log(response);
				this.curRep.provsvg = response["data"];
				var svg = new DOMParser().parseFromString(this.curRep.provsvg, 'application/xml').documentElement;
  				var el = document.getElementById("svg");
				
				while (el.firstChild) {
				     console.log("REMOVING");
				    el.removeChild(el.firstChild);
				}
  				el.appendChild( el.ownerDocument.importNode(svg, true));
			
				}
			)
			.catch(function(error) {console.log(error)});
		    },
		    triggerEdit: function (index) {
			this.curRep=this.templates[index];
			this.showModal = true;
			this.showAdd=false;
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/getTemplate", {'id':this.templates[index]['id']})
			.then( response => {
				this.curRep = response.data;
				console.log(response);
				}
			)
			.catch(function(error) {console.log(error)});
		    },
		    triggerAbout: function () {
			this.showAboutModal=true;
		    },
		    triggerAdd: function () {
			this.curRep={
			    title:"",
			    subject:"",
			    description:"",
			    type:"",
			    coverage:"",
			    comment:"",
			    creator:"",
			    };
			this.showModal=true;
			this.showAdd=true;
		    },
		    triggerDelete: function (index) {
			this.curRep=this.templates[index];
			this.showConfirmModal = true;
		    },
		    triggerDeleteConfirmed: function (template) {
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/deleteTemplate",
						{ 'id' : template['id'] }, 
						{ headers: this.createJwtHeaderData() }
			)
			.then( response => {
				this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/getTemplateList",
				{},
				{ headers: this.createJwtHeaderData() }
				)
				.then( response => { 
					this.templates = response.data;
					console.log(response); 
				})
				.catch(function(error) {console.log(error)})
			})
			.catch(function(error) {console.log(error)});
			this.showConfirmModal = false;
		    },
                    addNewTemplate: function (templatedata) {
			var createdTime=new Date().toLocaleString();
			templatedata["created"]=createdTime;
			templatedata["modified"]=createdTime;
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/addTemplate",
						{ 'info' : templatedata },
						{ headers: this.createJwtHeaderData() }
			)
			.then( response => {
				this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/getTemplateList",
				{},
				{ headers: this.createJwtHeaderData() }
				)
				.then( response => { 
					this.templates = response.data;
					console.log(response); 
				})
				.catch(function(error) {console.log(error)})
			})
			.catch(function(error) {console.log(error)});
			this.showModal = false;
			this.firstForm = true;
                    },
                    changeExistingTemplate: function (templatedata) {
			templatedata["modified"]=new Date().toLocaleString();
			this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/updateTemplate",
						{ 'info' : templatedata },
						{ headers: this.createJwtHeaderData() }
			)
			.then( response => {
				console.log(response);
				this.axiosInstance.post("https://envriplus-provenance.test.fedcloud.eu/getTemplateList",
				{},
				{ headers: this.createJwtHeaderData() }
				)
				.then( response => { 
					this.templates = response.data;
					console.log(response); 
				})
				.catch(function(error) {console.log(error)})
			})
			.catch(function(error) {console.log(error)});
			this.showModal = false;
                    }
                  }
        })
