const TopEngagementCard = {
    props: ["engagement"],
    data() {
        return {}
    },
    methods: {
        stringifyDate(date){
            return date
        },

    },
    template: `
    <div class="card mt-3 p-2">
        <div class="card-header mb-0">
            <div class="d-flex justify-content-between mb-1">
                <p class="font-h4 font-bold">{{engagement.name}}</p>
                <button class="btn btn-default btn-xs btn-table btn-icon__xs">
                    <i class="icon__18x18 icon-settings"></i>
                </button>
            </div>
            <div class="d-flex align-items-center">
                <div class="mr-3">
                    <img src="/issues/static/ico/circle.svg"> Green
                </div>
                <div class="d-flex align-items-center">
                    <i class="icon__18x18 icon-date-picker mr-1"></i>
                    <div>
                        {{stringifyDate(engagement.start_date)}} - {{stringifyDate(engagement.end_date)}}
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
}


