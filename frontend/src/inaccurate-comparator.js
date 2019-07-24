export default class InaccurateComparator {
    tolerance = 1e-10;

    static equals(a, b) {
        return (Math.abs(a - b) < this.tolerance);
    }

    static greaterThan(a, b) {
        return (a - b > -this.tolerance);
    }

    static lessThan(a, b) {
        return greaterThan(b, a);
    }
}