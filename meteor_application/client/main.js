import { Template } from 'meteor/templating';

import './main.html';

twitterData = new Mongo.Collection('oneYearData');
labels = new Mongo.Collection('label');
workers = new Mongo.Collection('worker');
hits = new Mongo.Collection('hit');


q3Options = ['GettingHired', 'GettingFired', 'QuitingJob', 'LosingJob', 'GettingPromotion', 'CutInHours', 'Other'];
tweetIDList = [];

workerID = "";
hitID = "";
assignmentID ="";

if(Meteor.isClient){
    var count = 0;
    var isComplete = false;

    //console.log("Client");
    Session.set('selectedTweet', -1);
    Session.set('q1', false);
    Session.set('q2', false);
    Session.set('q3', false);

    Template.content.onCreated( function() {
        this.subscribe( 'one_year_filtered', function() {
            $( ".loader" ).delay( 1 ).fadeOut( 'slow', function() {
                $( ".loading-wrapper" ).fadeIn( 'slow' );
            });
        });
    });


    Template.content.onRendered( function() {
        $( "svg" ).delay( 1000 ).fadeIn();
    });


    Template.content.helpers( {


        'validated': function () {
            function turkGetParam( name ) {
                var regexS = "[\?&]"+name+"=([^&#]*)";
                var regex = new RegExp( regexS );
                var tmpURL = fullurl;
                var results = regex.exec( tmpURL );
                if( results === null ) {
                    return "";
                } else {
                    return results[1];
                }
            }


            // Capture the URL
            var fullurl = window.location.href;

            assignmentID = turkGetParam('assignmentId');
            hitID = turkGetParam('hitId');
            workerID = turkGetParam('workerId');
            console.log(assignmentID);
            console.log(hitID);
            console.log(workerID);
            workers.insert({
                workerID: workerID,
                assignmentID: assignmentID,
                hitID: hitID
            });
            return !(workerID === "" || assignmentID === "");

        },

        'document': function () {

            if(Session.get('selectedTweet') === -1) {
                return twitterData.find().fetch()[count];
            }
            else {
                return twitterData.find().fetch()[Session.get('selectedTweet')];

            }

        },

        'backButton': function () {
            return Session.get('q1') && Session.get('q2') && Session.get('q3');
        },

        'completed': function () {
            if(Session.get('selectedTweet') === 3) {
                isComplete = true;
                hits.insert( {
                    hitID: hitID,
                    assignmentID: assignmentID,
                    workerID: workerID,
                    tweetList: tweetIDList
                })

            }
            return isComplete;
        }
    });


    Template.content.events( {
        'click .next': function (event, template) {
            var element1 = template.find('input:radio[name=q1]:checked');
            var element2 = template.find('input:radio[name=q2]:checked');
            var element3 = template.findAll('input:checkbox[name=q3]:checked');
            console.log("Selected options: " + $(element1).val() + " and " + $(element2).val() +
                " and " + $(element3).val());
            Session.set('selectedTweet',  count);
            Session.set('q1', false);
            Session.set('q2', false);
            Session.set('q3', false);


            var selectedBoxes = _.map(element3, function(item) {
                return item.defaultValue;
            });
            //console.log(selectedBoxes.length);

            function isChecked(selectedBoxes, q3Options, index) {
                for(var i=0; i<selectedBoxes.length; i++) {
                    if(selectedBoxes[i] === q3Options[index]) {
                        return 1;
                    }
                }
                return -1;
            }

            var checkboxResult = [];

            for(var idx=0; idx<q3Options.length; idx++) {
                var result = isChecked(selectedBoxes, q3Options, idx);
                checkboxResult.push({'option':q3Options[idx], 'checked': result});
            }


            console.log(checkboxResult);

            var indx = Session.get('selectedTweet');

            var data = twitterData.find().fetch()[indx];
            var tweetID = data['id'];
            var tweetText = data['text'];
            //console.log(data);
            tweetIDList.push(tweetID);

            labels.insert({
                    id: tweetID,
                    question1: $(element1).val(),
                    question2: $(element2).val(),
                    question3: checkboxResult
                }
            );

            count += 1;
            Session.set('selectedTweet',  count);

            template.find("form").reset();
        },

        'click .back': function (event, template) {
            count -= 1;
            Session.set('selectedTweet',  count);
            console.log(Session.get('selectedTweet'));
        }
    });


    Template.QandA.events({

        'change .qa': function (event, template) {

            var element1 = template.find('input:radio[name=q1]:checked');
            var element2 = template.find('input:radio[name=q2]:checked');
            var element3 = template.find('input:checkbox[name=q3]:checked');
            /*console.log("Selected options: " + $(element1).val() + " and " + $(element2).val() +
                " and " + $(element3).val()); */

            if($(element1).val() !== undefined) {
                Session.set('q1',  true);
            }

            if($(element2).val() !== undefined) {
                Session.set('q2',  true);
            }

            if($(element3).val() !== undefined) {
                Session.set('q3',  true);
            }

            if($(element3).val() === undefined) {
                Session.set('q3', false);
            }
        }


    });
}




