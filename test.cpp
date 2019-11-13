#include <iostream>
#include <vector>

using namespace std;

vector<int> vec = {1, 1, 3, 4};

bool vector_doppelte(vector<int> v)
{
    for (int i = 0; i < vec.size(); i++)
    {
        for (int j = 0; j < vec.size(); j++)
        {
            if (vec[i] == vec[j] && i != j)
            {
                return true;
            }
        }
    }
    return false;
}

int main()
{
    float a;
    cin >> a;

    cout << a;
    if (vector_doppelte(vec))
    {
        cout << "Es gibt doppelte\n";
    }
    else
    {
        cout << "Es gibt keine doppelten\n";
    }


    return 0;
}