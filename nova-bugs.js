// JavaScript Document

var app = angular.module("NovaBugs", []);

app.controller("BugCtrl", function ($scope) {
    $scope.priority = "High";
    $scope.orderList = "importance";
    $scope.filterSelection = "all";
    $scope.data = angular.fromJson(FileHelper.readStringFromFileAtPath("bugs.json"));
    $scope.raw_data = $scope.data.bugs;
    $scope.date = $scope.data.date;
    $scope.reverseSort = false;

    console.log($scope.date);
    for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
        try {
            $scope.raw_data[i].status_prio = "status" + $scope.raw_data[i].status.toUpperCase().replace(" ", "");
        }
        catch (exception) {
            $scope.raw_data[i].status_prio = "unspecified";
        }
        try {
            $scope.raw_data[i].prio_class = "importance" + $scope.raw_data[i].importance.toUpperCase();
        }
        catch (exception) {
            $scope.raw_data[i].importance_prio = "unknown";
        }
        $scope.raw_data[i].merged = 0;
        $scope.raw_data[i].abandoned = 0;
        $scope.raw_data[i].in_review = 0;
        for (var j = 0, jl = $scope.raw_data[i].reviews.length; j < jl; j++) {
            if ($scope.raw_data[i].reviews[j].status == "MERGED")
                $scope.raw_data[i].merged++;
            else if ($scope.raw_data[i].reviews[j].status == "ABANDONED")
                $scope.raw_data[i].abandoned++;
            else if ($scope.raw_data[i].reviews[j].status == "NEW")
                $scope.raw_data[i].in_review++;
        }
    }
    $scope.filtered_data = $scope.raw_data;


    $scope.FilterCtrl = function (value) {
        //$scope.filterSelection = value;
        $scope.filtered_data = [];
        console.log($scope.filterSelection);
        if ($scope.filterSelection == "all") {
            $scope.filtered_data = $scope.raw_data;
        }
        else {
            if ($scope.filterSelection == "stale") {
                filterStale();
            }
            else if ($scope.filterSelection == "update") {
                filterUpdated();
            }
            else if ($scope.filterSelection == "inProgress") {
                filterInProgress();
            }
            else if ($scope.filterSelection == "noOwner") {
                filterNoOwner();
            }
            else if ($scope.filterSelection == "ownerAbandoned") {
                filterOwnerAbandoned();
            }
            else if ($scope.filterSelection == "abandoned") {
                filterAbandoned();
            }
            else if ($scope.filterSelection == "merged") {
                filterMerged();
            }
            else if ($scope.filterSelection == "review") {
                filterReview();
            }
            else if ($scope.filterSelection == "undecided") {
                filterUndecided();
            }

        }
    };

    function filterUndecided() {
        for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
            var item = $scope.raw_data[i];
            if (item.importance == "unspecified") {
                $scope.filtered_data.push(item);
            }
        }
    }

    function filterReview() {
        filterInProgress();
        data = $scope.filtered_data;
        $scope.filtered_data = [];
        for (var i = 0, l = data.length; i < l; i++) {
            if (data[i].in_review > 0)
                $scope.filtered_data.push(data[i]);
        }
    }

    function filterAbandoned() {
        filterInProgress();
        data = $scope.filtered_data;
        $scope.filtered_data = [];
        for (var i = 0, l = data.length; i < l; i++) {
            if (data[i].merged == 0 && data[i].abandoned > 0 && data[i].in_review == 0)
                $scope.filtered_data.push(data[i]);
        }
    }

    function filterMerged() {
        filterInProgress();
        data = $scope.filtered_data;
        $scope.filtered_data = [];
        for (var i = 0, l = data.length; i < l; i++) {
            if (data[i].merged > 0 && data[i].abandoned == 0 && data[i].in_review == 0)
                $scope.filtered_data.push(data[i]);
        }
    }


    function filterStale() {
        for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
            var item = $scope.raw_data[i];
            if (item.stale == 1) {
                $scope.filtered_data.push(item);
            }
        }
    }

    function filterUpdated() {
        for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
            var item = $scope.raw_data[i];
            if (item.never_touched == 1) {
                $scope.filtered_data.push(item);
            }
        }
    }

    function filterInProgress() {
        for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
            var item = $scope.raw_data[i];
            if (item.status == "ASSIGNED") {
                $scope.filtered_data.push(item);
            }
        }
    }

    function filterNoOwner() {
        for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
            var item = $scope.raw_data[i];
            if (item.owner == "bugs@gluster.org") {
                $scope.filtered_data.push(item);
            }
        }
    }
    function filterOwnerAbandoned() {
        for (var i = 0, l = $scope.raw_data.length; i < l; i++) {
            var item = $scope.raw_data[i];
            if (item.owner != "bugs@gluster.org" && item.stale == 1) {
                $scope.filtered_data.push(item);
            }
        }
    }

});

function FileHelper() {
}
{
    FileHelper.readStringFromFileAtPath = function (pathOfFileToReadFrom) {
        var request = new XMLHttpRequest();
        request.open("GET", pathOfFileToReadFrom, false);
        request.send(null);
        var returnValue = request.responseText;

        return returnValue;
    };
}
