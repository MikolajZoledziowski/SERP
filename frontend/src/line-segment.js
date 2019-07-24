import InaccurateComparator from './inaccurate-comparator';

export default class LineSegment {

    constructor(x1, y1, x2, y2) {
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
    
        // Ax + By = C
        this.a = y2 - y1;
        this.b = x1 - x2;
        this.c = x1 * this.a + y1 * this.b;
    
        if (InaccurateComparator.equals(this.a, 0) && InaccurateComparator.equals(this.b, 0)) {
            throw new Error('Cannot construct a LineSegment with two equal endpoints.');
        }
    }

    intersect(that) {
        const d = (this.x1 - this.x2) * (that.y1 - that.y2) - (this.y1 - this.y2) * (that.x1 - that.x2);

        if (InaccurateComparator.equals(d, 0)) {
            // The two lines are parallel or very close.
            return {
                x: NaN,
                y: NaN
            };
        }

        const t1 = this.x1 * this.y2 - this.y1 * this.x2;
        const t2 = that.x1 * that.y2 - that.y1 * that.x2;
        const x = (t1 * (that.x1 - that.x2) - t2 * (this.x1 - this.x2)) / d;
        const y = (t1 * (that.y1 - that.y2) - t2 * (this.y1 - this.y2)) / d;
            
        const in1 = (InaccurateComparator.greaterThan(x, Math.min(this.x1, this.x2)) &&
                InaccurateComparator.lessThan(x, Math.max(this.x1, this.x2)) &&
                InaccurateComparator.greaterThan(y, Math.min(this.y1, this.y2)) &&
                InaccurateComparator.lessThan(y, Math.max(this.y1, this.y2)));
        
        const in2 = (InaccurateComparator.greaterThan(x, Math.min(that.x1, that.x2)) &&
                InaccurateComparator.lessThan(x, Math.max(that.x1, that.x2)) &&
                InaccurateComparator.greaterThan(y, Math.min(that.y1, that.y2)) &&
                InaccurateComparator.lessThan(y, Math.max(that.y1, that.y2)));

        return { x, y, in1, in2 };
    }

    x(y) {
        // x = (C - By) / a;
        if (this.a) {
            return (this.c - this.b * y) / this.a;
        } else {
            // a == 0 -> horizontal line
            return NaN;
        }
    }

    y(x) {
        // y = (C - Ax) / b;
        if (this.b) {
            return (this.c - this.a * x) / this.b;
        } else {
            // b == 0 -> vertical line
            return NaN;
        }
    }

    length() {
        return Math.sqrt(
            (this.y2 - this.y1) * (this.y2 - this.y1) +
            (this.x2 - this.x1) * (this.x2 - this.x1)
        );
    }

    offset(x, y) {
        return new LineSegment(
            this.x1 + x, this.y1 + y,
            this.x2 + x, this.y2 + y
        );
    };
}